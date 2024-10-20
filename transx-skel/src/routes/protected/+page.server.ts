import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.user) {
    throw redirect(307, '/auth/login');
  }

  return {
    user: locals.user
  };
};