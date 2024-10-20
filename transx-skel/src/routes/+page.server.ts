import type { PageServerLoad } from "./$types";
import { getSignInUrl } from "./server/helpers";

export const load = (async ({ locals }) => {
	const signInUrl = getSignInUrl();
	return { signInUrl, email: locals.user?.email };
}) satisfies PageServerLoad;