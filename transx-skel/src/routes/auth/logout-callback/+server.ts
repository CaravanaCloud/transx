//The callback route is an API route, not a page.
//It is called by the OAuth provider after the user logout.

import type { RequestHandler } from './$types';
import { logoutUser } from '../../server/helpers';
import { redirect } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ cookies, locals }) => {
    // Chama a função para fazer logout do usuário
    logoutUser(cookies, locals);

    // Redireciona o usuário para a página de login ou outra página apropriada
    throw redirect(307, '/');
};