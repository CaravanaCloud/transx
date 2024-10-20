// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
// and what to do when importing types
import { User } from "./types";
declare namespace App {
	interface Locals {
		user?: User;
	}
	// interface PageData {}
	// interface Error {}
	// interface Platform {}
}
