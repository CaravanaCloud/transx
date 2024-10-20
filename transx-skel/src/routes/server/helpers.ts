// Importar o módulo dotenv para carregar variáveis de ambiente de um arquivo .env
import dotenv from 'dotenv';
import type { Cookies } from '@sveltejs/kit';
import type { Locals } from '../../types'; // Importe a interface Locals

// Carregar variáveis de ambiente do arquivo .env
dotenv.config({ path: '../.envrc' });
// Definir a interface para as variáveis de ambiente esperadas
interface Env {
  COGNITO_BASE_URI: string;
  COGNITO_CLIENT_ID: string;
  CF_PAGES_URL: string;
  AUTH_COGNITO_SECRET: string;
}

// Acessar as variáveis de ambiente
const env: Env = {
  COGNITO_BASE_URI: process.env.COGNITO_BASE_URI!,
  COGNITO_CLIENT_ID: process.env.COGNITO_CLIENT_ID!,
  CF_PAGES_URL: process.env.CF_PAGES_URL!,
  AUTH_COGNITO_SECRET: process.env.AUTH_COGNITO_SECRET!
};


/**
 * Generate the URL to redirect the user to for signing in.
 * @see https://docs.aws.amazon.com/cognito/latest/developerguide/login-endpoint.html
 */
export function getSignInUrl(): string {
	const baseUrl = env.COGNITO_BASE_URI;
	const clientId = env.COGNITO_CLIENT_ID;
	if (!baseUrl || !isValidUrl(baseUrl)) {
		throw new Error(`Invalid base URL: ${baseUrl}`);
	  }

	// The login api endpoint with the required parameters.
	const loginUrl = new URL("/login", baseUrl);
	loginUrl.searchParams.set("response_type", "code");
	loginUrl.searchParams.set("client_id", clientId);
	loginUrl.searchParams.set("redirect_uri", getLoginRedirectUrl());
	loginUrl.searchParams.set("scope", "email openid phone");
	return loginUrl.toString();
}

// todo adjust uri in cognito and here
export function getSignOutUrl(): string {
	const baseUrl = env.COGNITO_BASE_URI;
	const clientId = env.COGNITO_CLIENT_ID;

	const logoutUrl = new URL("/logout", baseUrl);
	// logoutUrl.searchParams.set("response_type", "code");
	logoutUrl.searchParams.set("client_id", clientId);
	logoutUrl.searchParams.set("logout_uri", getLogoutRedirectUrl());

	return logoutUrl.toString();
}

/**
 * Make sure that the redirect URL is always the same as the one configured in Cognito.
 */
function getLoginRedirectUrl(): string {
	return new URL("/auth/login-callback/", env.CF_PAGES_URL).toString();
}
function getLogoutRedirectUrl(): string {
	return new URL("/auth/logout-callback/", env.CF_PAGES_URL).toString();
}


function isValidUrl(urlString: string): boolean {
  try {
    new URL(urlString);
    return true;
  } catch {
    return false;
  }
}

//token treatment
interface Tokens {
	access_token: string;
	id_token: string;
	token_type: "Bearer";
	expires_in: number;
	refresh_token?: string;
}

interface TokenPayload {
    // Are we passing an auth code or a refresh token
	grant_type: "authorization_code" | "refresh_token";
	client_id: string;
	client_secret: string;
	redirect_uri: string;
	code?: string;
	refresh_token?: string;
}

interface TokenOptionsCode {
	code: string;
	refreshToken?: never;
}

interface TokenOptionsRefresh {
	code?: never;
	refreshToken: string;
}

type TokenOptions = TokenOptionsCode | TokenOptionsRefresh;
/**
 * This function can either generate tokens from a code or from a refresh token.
 * If a code is provided, this all tokens is generated (requires a fresh login)
 * If a refresh token is provided, only the access/id token is updated.
 * @see https://docs.aws.amazon.com/cognito/latest/developerguide/token-endpoint.html
 */
export async function getTokens(options: TokenOptions) {
	const baseUrl = env.COGNITO_BASE_URI;
	const clientId = env.COGNITO_CLIENT_ID;
	const clientSecret = env.AUTH_COGNITO_SECRET;

	//generate the authorization geader value (basic auth) using the cognito client id and secret
	const authHeader = btoa(`${clientId}:${clientSecret}`); // for client side
	// const authHeader = Buffer.from(`${clientId}:${clientSecret}`).toString("base64"); server side

	// token api endpoint
	const url = new URL("/oauth2/token/", baseUrl);

	//bodyObject 
	const bodyObject: TokenPayload = {
		// If a code is passed, use the authorization_code grant Type.
		// If a refresh token is passed, use the refresh_token grant Type.
		grant_type: options.code ? "authorization_code" : "refresh_token",
		client_id: clientId,
		client_secret: clientSecret,	
		redirect_uri: getLoginRedirectUrl(),
	};	
	// add the code or refresh token to the body object depending on the options
	if(options.code) {
		bodyObject.code = options.code;
	} 
	if (options.refreshToken) {
		bodyObject.refresh_token = options.refreshToken;
	}

	//serializer
	const body: string = Object.entries(bodyObject)
		.map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
		.join("&");

	const response = await fetch(url.toString(), {
		method: "POST",
		headers: {
			// headres defined n codnito docs
			"Content-Type": "application/x-www-form-urlencoded",
			Authorization: `Basic ${authHeader}`,

		},
		body
	});
	return (await response.json()) as Tokens;
}

export function logoutUser(cookies: Cookies, locals: Locals): void {
    // Deletar cookies de autenticação
 // Deletar o cookie `id_token` definindo seu valor vazio e Max-Age=0
    cookies.set('id_token', '', {
        path: '/', // Certifique-se de que o path corresponda ao usado no cookie original
        maxAge: 0, // Isso expira imediatamente o cookie
        httpOnly: true, // Se o cookie foi definido como HttpOnly
        secure: true, // Certifique-se de usar `secure` se estiver usando HTTPS
        sameSite: 'lax' // Política SameSite apropriada
    });

    // Deletar o cookie `refresh_token`
    cookies.set('refresh_token', '', {
        path: '/', // Certifique-se de que o path corresponda ao usado no cookie original
        maxAge: 0, // Expira o cookie
        httpOnly: true,
        secure: true,
        sameSite: 'lax'
    });

    // Definir `locals.user` como null para limpar a sessão do usuário
    locals.user = null;
    // Definir event.locals.user como null
    locals.user = null;

    console.log('Usuário deslogado e cookies deletados.');
}