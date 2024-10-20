import type { PageServerLoad } from "./$types";
import { getSignInUrl, getSignOutUrl } from "./server/helpers";

export const load = (async ({ locals }) => {
	const signInUrl = getSignInUrl();
	const signOutUrl = getSignOutUrl();

	return { signInUrl, signOutUrl, email: locals.user?.email };
}) satisfies PageServerLoad;