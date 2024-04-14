package transx;

import static org.awaitility.Awaitility.await;
import static software.amazon.awssdk.services.transcribe.model.TranscriptionJobStatus.COMPLETED;
import static software.amazon.awssdk.services.transcribe.model.TranscriptionJobStatus.FAILED;

import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Duration;
import java.util.LinkedList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Stream;


import io.quarkus.logging.Log;
import jakarta.inject.Inject;
import picocli.CommandLine.Command;
import software.amazon.awssdk.services.iam.IamClient;
import software.amazon.awssdk.services.iam.model.AttachRolePolicyRequest;
import software.amazon.awssdk.services.iam.model.CreateRoleRequest;
import software.amazon.awssdk.services.iam.model.GetRoleRequest;
import software.amazon.awssdk.services.iam.model.NoSuchEntityException;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.services.transcribe.TranscribeClient;
import software.amazon.awssdk.services.transcribe.model.Media;
import software.amazon.awssdk.services.transcribe.model.MediaFormat;
import software.amazon.awssdk.services.transcribe.model.StartTranscriptionJobRequest;
import software.amazon.awssdk.services.transcribe.model.SubtitleFormat;
import software.amazon.awssdk.services.transcribe.model.Subtitles;
import software.amazon.awssdk.services.translate.TranslateClient;
import software.amazon.awssdk.services.translate.model.DescribeTextTranslationJobRequest;
import software.amazon.awssdk.services.translate.model.JobStatus;
import software.amazon.awssdk.services.translate.model.StartTextTranslationJobRequest;
import software.amazon.awssdk.services.translate.model.TextTranslationJobProperties;

@Command(name = "transx", mixinStandardHelpOptions = true)
public class TransxCommand implements Runnable {
    S3Client s3 = S3Client.create();
    TranscribeClient transcribe = TranscribeClient.create();
    TranslateClient translate = TranslateClient.create();
    IamClient iam = IamClient.builder().build();
    Subtitles srt = Subtitles.builder().formats(SubtitleFormat.SRT).build();

    @Inject
    TransxConfig cfg;

    @Override
    public void run() {
        var directoryPath = loadPath();
        var queue = new LinkedList<Path>();
        try (Stream<Path> paths = Files.walk(Paths.get(directoryPath))) {
            paths.filter(Files::isRegularFile)
                    .filter(path -> path.toString().endsWith(".mp4"))
                    .forEach(queue::add);
        } catch (Exception e) {
            e.printStackTrace();
        }
        Log.infof("[%s] videos queued for transcription", queue.size());
        var bucketName = getBucketName();
        loadBucket(bucketName);
        
        var puts = queue.stream()
                .map(p -> putObject(bucketName, p))
                .filter(Optional::isPresent)
                .map(Optional::get);
        var putsList = puts.toList();
        Log.infof("[%s] videos uploaded to S3", putsList.size());
        var transcribed = putsList.stream().map(this::transcribe);
        var transcribeList = transcribed.toList();
        Log.infof("[%s] Transcriptions done", transcribeList.size());
        var translated = transcribeList.stream().map(this::translate);
        var translatedList = translated.toList();
        Log.infof("[%s] Translation done", translatedList.size());
        translatedList.stream().forEach(t -> download(t));
        Log.infof("Transx done");
    }

    private String loadPath() {
        return cfg.path().orElseGet(this::cwd);
    }

    private void download(TranslateResult t) {
        var key = t.mediaKey();
        var prefix = t.outputPrefix();
        var langs = cfg.targetLanguages().stream().map(l -> l.toLowerCase());
        var path = t.path();
        var parent = path.getParent();
        langs.forEach(l -> download(parent, prefix, key, l));
    }

    private String download(Path dir, String prefix, String key, String lang) {
        var s3Key = lang + "." + key + ".srt";
        var keyPath = prefix+ "/" + s3Key;
        var uri = "s3://" + getBucketName() + "/" + keyPath;
        Log.infof("Downloading %s", uri);
        var req = GetObjectRequest.builder()
            .bucket(getBucketName())
            .key(key)
            .build();
        var path = dir.resolve(lang + "." + key + ".srt");
        var bytes = s3.getObjectAsBytes(req);
        try (var fos = new FileOutputStream(Paths.get(keyPath).toFile())) {
            fos.write(bytes.asByteArray());
            Log.infof("File downloaded successfully: " + path.toString());
        } catch (IOException e) {
           Log.warnf("Unable to write file: " + e.getMessage());
        }
        return key;
    }

    private String getRoleName() {
        return "TrasnxRole1";
    }

    public String loadRole(String roleName) {
        var req = GetRoleRequest.builder()
                .roleName(roleName)
                .build();
        try {
            var resp = iam.getRole(req);
            Log.infof("Role found");
            return resp.role().arn();
        } catch (NoSuchEntityException e) {
            return createRole(roleName);
        }
    }

    private String createRole(String roleName) {
        Log.info("Creating role");
        var req = CreateRoleRequest.builder()
                .roleName(roleName)
                .assumeRolePolicyDocument(getTrustPolicy())
                .build();
        var resp = iam.createRole(req);
        List.of(
            "arn:aws:iam::aws:policy/AmazonTranscribeFullAccess",
            "arn:aws:iam::aws:policy/AmazonS3FullAccess")
            .forEach(policy -> attachPolicy(roleName, policy));
        return resp.role().arn();
    }

    private void attachPolicy(String roleName, String policyArn) {
        var req = AttachRolePolicyRequest.builder()
            .roleName(roleName)
            .policyArn(policyArn)
            .build();
        iam.attachRolePolicy(req);
    }

    private String getTrustPolicy() {
        var policy = """
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Effect": "Allow",
                      "Principal": {
                        "Service": "translate.amazonaws.com"
                      },
                      "Action": "sts:AssumeRole"
                    }
                  ]
                }
        """;
        return policy;
    }

    private TranslateResult translate(TranscribeResult result) {
        var bucketName = getBucketName();
        var prefix = result.mediaPrefix();
        var s3Prefix = "s3://" + bucketName + "/" + prefix;
        var inputURI =  s3Prefix + "/transcribe/";
        var outputURI = s3Prefix + "/translate/";
        Log.infof("Translating %s", inputURI);
        
        var req = StartTextTranslationJobRequest.builder()
                .inputDataConfig(builder -> 
                    builder.s3Uri(inputURI)
                    .contentType("text/plain"))
                .outputDataConfig(builder -> builder.s3Uri(outputURI))
                .targetLanguageCodes(cfg.targetLanguages())
                .dataAccessRoleArn(getRoleArn())
                .sourceLanguageCode(getSourceLangCode())
                .build();
        var resp = translate.startTextTranslationJob(req);
        var jobId = resp.jobId();
        awaitTranslation(jobId);
        var job = getTranslateJob(jobId);
        var outputPrefix = job.outputDataConfig().s3Uri();
        return new TranslateResult(result, outputPrefix);
    }

    private String getRoleArn() {
        var roleName = getRoleName();
        var roleARN = loadRole(roleName);
        return roleARN;
    }

    private String getSourceLangCode() {
        return cfg.sourceLanguage();
    }

    private void awaitTranslation(String jobId) {
        await()
            .timeout(Duration.ofMinutes(45))
            .pollInterval(Duration.ofSeconds(30))
            .until(() -> translateDone(jobId));
    }

    private boolean translateDone(String jobId) {
        var props = getTranslateJob(jobId);
        var status = props.jobStatus();
        var done = JobStatus.COMPLETED.equals(status)
                || JobStatus.COMPLETED_WITH_ERROR.equals(status)
                || JobStatus.FAILED.equals(status);
        Log.infof("Status [%s] for translation [%s]", status, jobId);
        return done;
    }

    private TextTranslationJobProperties getTranslateJob(String jobId) {
        var req = DescribeTextTranslationJobRequest.builder()
                .jobId(jobId)
                .build();
        var resp = translate.describeTextTranslationJob(req);
        var props = resp.textTranslationJobProperties();
        return props;
    }

    private TranscribeResult transcribe(ObjectPutResult putResult) {
        var bucketName = getBucketName();
        var key = putResult.key();
        var mediaURL = "s3://" + bucketName + "/" + key;
        Log.infof("Transcribing %s", mediaURL);
        var media = Media.builder().mediaFileUri(mediaURL).build();
        var timestamp = "" + System.currentTimeMillis();
        var jobName = ("Transcribe_" + key + "_" + timestamp)
                .replace(".mp4", "")
                .replaceAll("[^0-9a-zA-Z._-]", "_");
        var mediaKey = normalize(key.replace(".mp4", ""));
        var outputPrefix = jobName + "/transcribe/";
        var outputKey = outputPrefix + mediaKey;
        var req = StartTranscriptionJobRequest.builder()
                .transcriptionJobName(jobName)
                .identifyMultipleLanguages(true)
                .media(media)
                .mediaFormat(MediaFormat.MP4)
                .outputBucketName(bucketName)
                .outputKey(outputKey)
                .subtitles(srt)
                .build();
        transcribe.startTranscriptionJob(req);
        awaitTranscriptionDone(jobName);
        var result = new TranscribeResult(putResult, jobName, mediaKey);
        return result;
    }

    private String normalize(String str) {
        return str.replaceAll("[^0-9a-zA-Z._-]", "_");
    }

    private void awaitTranscriptionDone(String jobName) {
        await()
                .timeout(Duration.ofMinutes(5))
                .pollInterval(Duration.ofSeconds(15))
                .until(() -> transcriptionDone(jobName));
    }

    private Boolean transcriptionDone(String jobName) {
        var resp = transcribe.getTranscriptionJob(builder -> builder.transcriptionJobName(jobName));
        var status = resp.transcriptionJob().transcriptionJobStatus();
        var done = COMPLETED.equals(status) || FAILED.equals(status);
        Log.infof("Status [%s] for transcription [%s]", status, jobName);
        return done;
    }

    public Optional<ObjectPutResult> putObject(String bucketName, Path path) {
        Log.infof("Put object to S3 %s", path);
        var file = path.toFile();
        if (!file.exists()) {
            Log.errorf("File %s does not exist", path);
            return Optional.empty();
        }

        var keyName = path.getFileName().toString();
        var req = PutObjectRequest.builder().bucket(bucketName).key(keyName).build();
        var resp = s3.putObject(req, path);
        var result = new ObjectPutResult(path, keyName);
        return Optional.of(result);
    }

    private void loadBucket(String bucketName) {
        var exists = s3.listBuckets()
                .buckets()
                .stream()
                .anyMatch(bucket -> bucket.name().equals(bucketName));
        if (!exists) {
            s3.createBucket(b -> b.bucket(bucketName));
        }
    }

    private String getBucketName() {
        return cfg.bucketName().orElse("transx-bucket-"+System.currentTimeMillis());
    }

    public void transcribe(Path path) {
        Log.infof("Transcribing %s", path);

    }

    private String cwd() {
        return System.getProperty("user.dir");
    }

}
