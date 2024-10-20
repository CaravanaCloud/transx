/** 
* For the parseJWT function you can use any npm JWT library
* or one line of js:
* JSON.parse(Buffer.from(token.split(".")[1], "base64").toString());
**/
import type { Handle } from "@sveltejs/kit";
import { parseJwt } from "./routes/server/utils";
import { getTokens, getSignOutUrl } from "./routes/server/helpers";
import { redirect } from "@sveltejs/kit";
export const  handle: Handle = (async ({ event, resolve }) => {
	// Try to get the id token from the cookie
	const rawIdToken = event.cookies.get("id_token");
	if (rawIdToken) {
		// If the id token exists, parse it and add it to the locals
		const idToken = parseJwt<{ email: string; exp: number }>(rawIdToken);
		event.locals.user = { email: idToken.email };
	}

	// Handle protected routes
	if (event.url.pathname.startsWith("/protected")) {
		// If the user is not logged in (no id token)
		if (!event.locals.user) {
			// Get the refresh token
			const refreshToken = event.cookies.get("refresh_token");
			if (!refreshToken) {
				// if the refresh token doesn't exist
				// redirect to sign out and sign in again
				const signOutUrl = getSignOutUrl();
				throw redirect(307, signOutUrl);
			}

			try {
				// Try to update the tokens
				const updatedTokens = await getTokens({ refreshToken: refreshToken });
				// Update the cookie for the id token
				const idExpires = new Date();
				idExpires.setSeconds(idExpires.getSeconds() + updatedTokens.expires_in);
				event.cookies.set("id_token", updatedTokens.id_token, { path: "/", expires: idExpires });

				// And the locals
				const idToken = parseJwt<{ email: string; exp: number }>(updatedTokens.id_token);
				event.locals.user = { email: idToken.email };
				console.log("User refreshed", event.locals.user);
			} catch (error) {
				// If the refresh token is invalid
				// redirect to sign out and sign in again
				const signOutUrl = getSignOutUrl();
				throw redirect(307, signOutUrl);
			}

			// Carry on
			
		}
	}

	const response = await resolve(event);
	return response;
});