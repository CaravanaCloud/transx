// /**
//  * @file src/hooks.service.ts
//  * File containing the hooks service
//  */



import { SvelteKitAuth } from '@auth/sveltekit';
import Cognito from '@auth/sveltekit/providers/cognito';

// set AUTH_COGNITO_ID
// AUTH_COGNITO_SECRET
// AUTH_COGNITO_ISSUER
export const { handle, signIn, signOut } = SvelteKitAuth({
  providers: [Cognito],
})


// // Import the SvelteKit Auth module
// import { SvelteKitAuth } from "@auth/sveltekit"
// import Credentials from "@auth/core/providers/credentials"
// // Import the Cognito service that we created earlier
// import { getSession, refreshAccessToken, type CognitoUserSessionType } from "$lib/domains/auth/services/Cognito"

// import type { Handle } from '@sveltejs/kit';
// // Type of the user object returned from the Cognito service
// import type AuthUser from "$lib/domains/auth/types/AuthUser";
// // Import the secret key from the environment variables
// import { AUTH_SECRET } from "$env/static/private";
// // interface AuthToken {
// //   accessToken: string;
// //   accessTokenExpires: number;
// //   refreshToken: string;
// //   user: {
// //     id: string;
// //     name: string;
// //     email: string;
// //   };
// // }
// /**
//  * Extract the user object from the session data. This is a helper function that we will use to extract the user object from the session data returned from the Cognito service.
// //  */
// // const extractUserFromSession = (session: CognitoUserSessionType): AuthUser => {
// //   if (!session?.isValid?.()) throw new Error('Invalid session');
// //   const user = session.getIdToken().payload;
// //   return {
// //     id: user.sub,
// //     name: `${user.name} ${user.family_name}`,
// //     email: user.email,
// //     image: user.picture,
// //     accessToken: session.getAccessToken().getJwtToken(),
// //     accessTokenExpires: session.getAccessToken().getExpiration(),
// //     refreshToken: session.getRefreshToken().getToken(),
// //   }
// // }
// /**
//  * Create the token object from the user object. This is a helper function that we will use to create the token object from the user object returned from the Cognito service.
//  */
// // const createTokenFromUser = (user: AuthUser): AuthToken => {
// //   return {
// //     accessToken: user.accessToken,
// //     accessTokenExpires: user.accessTokenExpires,
// //     refreshToken: user.refreshToken,
// //     user: {
// //       id: user.id,
// //       name: user.name,
// //       email: user.email,
// //       image: user.image,
// //     },
// //   }
// // }
// export const handle = SvelteKitAuth({
//   secret: AUTH_SECRET,
//   providers: [
//     Credentials({
//       type: 'credentials',
//       id: 'ourcredentials',
//       name: 'ournameCognito',
//       credentials: {
//         email: { label: "Email", type: "email", placeholder: "test@test.com" },
//         password: { label: "Password", type: "password" },
//       },
//       async authorize(credentials) {
//         if (!credentials) return null
//         try {
//           const response = await getSession(credentials?.email, credentials?.password)
//           return extractUserFromSession(response)
//         } catch (error) {
//           console.error(error);
//           return null
//         }
//       }
//     }) as any,
//   ],
//   /**
//    * Since we are using custom implementation; we have defined URLs for the login and error pages
//    */
//   pages: {
//     signIn: "/auth/login",
//     error: "/auth/login",
//   },
//   callbacks: {
//     /**
//      * This callback is called whenever a JWT is created or updated. 
//      * For the first time login we are creating a token from the user object returned by the authorize callback.
//      * For subsequent requests we are refreshing the access token and creating a new token from the user object. If the refresh token has expired
//      *
//      */
//     async jwt({ token, user, account }: any) {
//       // Initial sign in; we have plugged tokens and expiry date into the user object in the authorize callback; object
//       // returned here will be saved in the JWT and will be available in the session callback as well as this callback
//       // on next requests
//       if (account && user) {
//         return createTokenFromUser(user);
//       }
//       // Return previous token if the access token has not expired yet
//       if (Date.now() < token?.accessTokenExpires) {
//         return token;
//       }
//       try {
//         const newUserSession = await refreshAccessToken({
//           refreshToken: token?.refreshToken,
//         })
//         const user = extractUserFromSession(newUserSession);
//         return createTokenFromUser(user);
//       } catch(error) {
//         console.error(error);
//         throw new Error('Invalid session');
//       }
//     },
//     /**
//      * The session callback is called whenever a session is checked. By default, only a subset of the token is
//      * returned for increased security. We are sending properties required for the client side to work.
//      * 
//      * @param session - Session object
//      * @param token - Decrypted JWT that we returned in the jwt callback
//      * @returns - Promise with the result of the session
//      */
//     async session({ session, token }: any) {
//       session.user = token.user
//       session.accessToken = token.accessToken
//       session.error = token.error
//       return session;
//     },
//   },
// });