<script lang="ts">
	let operations: string[] = [];
	let operationTranscribe: boolean = false;
	let fileName: string = '';
	let file: File | null = null;

	const handleSubmit= () => {
		console.log(`***** operations: ${operations}, filename: ${fileName}, File:`, file);
		// TODO connect custom send to backend process
	};
</script>

<div class="container h-full mx-auto flex justify-center items-center">
	<div class="space-y-10 text-center flex flex-col items-center">
			<form on:submit|preventDefault={handleSubmit} class="space-y-10 flex flex-col ">
				<input placeholder="File name" class="input variant-form-material" bind:value={fileName} />
			<div class="space-y-2">
				<label class="flex items-center space-x-2">	
					<input class="checkbox" type="checkbox" bind:group={operations} value="translate"/>
					<p>Translate</p>
				</label>
				<label class="flex items-center space-x-2">
					<input class="checkbox" type="checkbox" bind:group={operations} value="transcribe"/>
					<p>Transcribe</p>
				</label>
			</div>
			<div class="space-y-10 text-center flex flex-col items-center">
				<input class="input" type="file" bind:value={file} />
			</div>
			<button type="submit" class="btn variant-filled">Submit</button>
		</form>
	</div>
</div>
