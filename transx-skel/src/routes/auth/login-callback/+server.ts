//The callback route is an API route, not a page.
//It is called by the OAuth provider after the user has authenticated.
//It receives the OAuth token and the user's profile.
//It then creates a session for the user and redirects to the home page.
//This route is called by the OAuth provider after the user has authenticated.

import type { RequestHandler } from "./$types";
import { getTokens } from "../../server/helpers";
import { error, redirect } from "@sveltejs/kit";


export const GET: RequestHandler = async ({ url, cookies }) => {
    const code = url.searchParams.get("code");
    console.log('url:', url);

    if (!code) {
        throw error(500, "Missing code parameter");
    }

    let tokens = null;
    try {
        tokens = await getTokens({ code });
        console.log('tokens:', tokens);
    } catch (err) {
        console.error(err);
        return new Response(JSON.stringify(err), { status: 500 });
    }


    if (tokens && tokens.access_token && tokens.id_token && tokens.refresh_token) {
        // Set the expire time for the refresh token
        // This is set in the Cognito console to 30 days by default
        // so we'll use 29 days here.
        // When the refresh token expires, the user will
        // have to log in again
        const refreshExpires = new Date();
        refreshExpires.setDate(refreshExpires.getDate() + 29);
        cookies.set("refresh_token", tokens.refresh_token, {
            path: "/",
            expires: refreshExpires
        });

        //Get the expire time for id token
        // and set cookies

        const idExpires = new Date();
        idExpires.setSeconds(idExpires.getSeconds() + tokens.expires_in);
        cookies.set("id_token", tokens.id_token, { path: "/", expires: idExpires });

        // Redirect back to the home page
        throw redirect(307, "/");
    } else {
        return new Response(JSON.stringify(tokens), { status: 500 });
    }
};