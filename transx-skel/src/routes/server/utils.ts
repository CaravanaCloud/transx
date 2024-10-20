
/** 
* For the parseJWT function you can use any npm JWT library
* or one line of js:
* JSON.parse(Buffer.from(token.split(".")[1], "base64").toString());
**/
export function parseJwt<T>(token: string): T {
    return JSON.parse(Buffer.from(token.split(".")[1], "base64").toString());
} 
