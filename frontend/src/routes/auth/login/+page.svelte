<script lang="ts">
	import { auth } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import logo from '$lib/assets/LOGO.png';
	import left from '$lib/assets/AUTH/DESIGN.png';
	import { Mail, Eye, EyeClosed } from '@lucide/svelte';

	let credential = $state('');
	let password = $state('');
	let loading = $state(false);
	let showPassword = $state(false);

	async function handleLogin(e: Event) {
		e.preventDefault();
		if (!credential.trim() || !password) {
			toast.error('Enter your username/email and password.');
			return;
		}
		loading = true;
		try {
			await auth.login(credential.trim(), password);
			toast.success('Logged in successfully!');
			const role = auth.role;
			const routes: Record<string, string> = {
				admin: '/admin',
				agent: '/agent',
				customer: '/portal',
				finance_staff: '/finance_staff',
				service_staff: '/service_staff',
				service_advisor: '/service_staff'
			};
			goto(role ? routes[role] || '/' : '/');
		} catch (err: any) {
			toast.error(err.message || 'Login failed.');
		} finally {
			loading = false;
		}
	}
</script>
<header>
	<title>Login</title>
</header>
<div class="container">
	<div class="left_side">
		<div class="bg">
			<img src={left} alt="background" class="img_bg" width="500">
		</div>
	</div>

	<div class="right_side">
		<div class="r_container">
			<!-- LOGO & HEADING -->
			<div class="sec_1">
				<div class="heading">
					<img src={logo} alt="Logo" width="300" >
					<h1>Sign in to your Account</h1>
					<span style="color:gray;">Enter your details to proceed further</span>
				</div>
			</div>

			<!-- INPUTS -->
			<form class="sec_2" onsubmit={handleLogin}>
				<label for="email">
					Email or Username
					<div class="input-wrap">
						<div class="email_icon">
							<Mail  size={18} />
						</div>
						<input type="text" bind:value={credential} placeholder="Email or username" class="email">
					</div>
				</label>
				<label for="password">
					Password
					<div class="input-wrap">
						<input type={showPassword ? 'text' : 'password'} id="password" bind:value={password} placeholder="Password" class="password">
						<button type="button" class="toggle-pw" onclick={() => showPassword = !showPassword} tabindex="-1">
							{#if showPassword}
								<EyeClosed size={18} />
							{:else}
								<Eye size={18} />
							{/if}
						</button>
					</div>
				</label>
				<label style="margin-top: 1rem;">
					<input type="submit" value={loading ? 'Signing in...' : 'Sign in'} disabled={loading}>
				</label>
			</form>

			<!-- RECOVER & HOW TO GET AN ACCOUNT -->
			<div class="sec_3">
				<a href="/auth/forgot-password">Forgot Password</a>
				<a href="/auth/how_to_get_an_account">How to get an Account?</a>
			</div>
		</div>
	</div>
</div>

<style>
.container {
	display: flex;
	justify-content: space-around;
	padding: 5rem 3rem;

	.left_side {
		height: 100%;
		width: 100%;
		display: grid;
		place-items: center;
		padding-left: 8rem;

		.img_bg {
			border-radius: 20px;
			width: 720px;
			height: 750px;
		}
	}

	.right_side {
		height: 100%;
		width: 100%;
		padding-right: 7rem;
		.r_container {
			width: 400px;
			display: flex;
			flex-direction: column;
			justify-content: center;
			align-items: center;
			padding-left: 4rem;
			padding-top: 5rem;
			gap: 2rem;

			.heading {
				display: flex;
				flex-direction: column;
				justify-content: center;
				align-items: center;
			}

			.sec_2 {
				width: 350px;
				display: flex;
				flex-direction: column;
				gap: 1.3rem;

				label {
					display: flex;
					flex-direction: column;
					gap: 4px;
					font-size: 14px;
					color: #333;
				}

				.input-wrap {
					position: relative;
					width: 100%;
				}

				.email_icon{
					position: absolute;
					right: 12px;
					top: 50%;
					transform: translateY(-50%);
					color: #989898;
					pointer-events: none;
				}

				.email,
				.password {
					width: 100%;
					height: 42px;
					margin-top: 3px;
					padding: 0.5rem;
					box-sizing: border-box;
				}

				/* Email has left icon */
				.email {
					width: 100%;
					height: 42px;
					padding-right: 40px; /* space for mail icon */
					box-sizing: border-box;
				}

				/* Password has eye icon on right */
				.password {
					width: 100%;
					height: 42px;
					padding-right: 40px; /* space for eye icon */
					box-sizing: border-box;
				}

				.toggle-pw {
					position: absolute;
					right: 12px;
					top: 50%;
					transform: translateY(-50%);
					background: none;
					border: none;
					cursor: pointer;
					color: #989898;
					display: flex;
					align-items: center;
				}

				.toggle-pw:hover {
					color: #0d76ff;
				}

				input[type='submit'] {
					width: 100%;
					height: 50px;
					margin-top: -18px;
					background-color: #0d76ff;
					border: transparent;
					border-radius: 4px;
					color: white;
					font-weight: bold;
					font-size: 1.1rem;
					transition: all 0.3s ease-in-out;
					cursor: pointer;
					box-sizing: border-box;

					&:hover:not(:disabled) {
						opacity: 0.8;
					}

					&:disabled {
						opacity: 0.6;
						cursor: not-allowed;
					}
				}
			}

			.sec_3 {
				width: 100%;
				margin-left: 1.2rem;
				display: flex;
				justify-content: space-around;
				gap: 2rem;

				a {
					color: #0d76ff;
				}
			}
		}
	}
}


</style>
