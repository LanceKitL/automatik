<script lang="ts">
	import { forgotPassword } from '$lib/services/api';
	import { toast } from 'svelte-sonner';
	import logo from '$lib/assets/LOGO.png';
	import left from '$lib/assets/AUTH/DESIGN.png';
	import { Mail } from '@lucide/svelte';

	let email = $state('');
	let loading = $state(false);
	let sent = $state(false);

	async function handleSubmit(e: Event) {
		e.preventDefault();

		if (!email.trim()) {
			toast.error('Please enter your email address.');
			return;
		}

		loading = true;
		try {
			await forgotPassword(email.trim());
			toast.success('Reset link sent! Check your email.');
			sent = true;
		} catch (err) {
			toast.error(err instanceof Error ? err.message : 'Something went wrong.');
		} finally {
			loading = false;
		}
	}
</script>
<svelte:head>
	<title>Forgot Password</title>
</svelte:head>
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
					<h1>Reset your Password</h1>
					<span style="color:gray;">Enter your email to receive a reset link</span>
				</div>
			</div>

			<!-- INPUTS -->
			<form class="sec_2" onsubmit={handleSubmit}>
				<label for="email">
					Email
					<div class="input-wrap">
						<div class="email_icon">
							<Mail size={18} />
						</div>
						<input
							type="email"
							id="email"
							bind:value={email}
							placeholder="Enter your email"
							class="email"
							required
							disabled={loading}
						>
					</div>
				</label>

				<label>
					<input
						type="submit"
						value={loading ? 'Sending...' : 'Send Reset Link'}
						disabled={loading}
					>
				</label>
			</form>

			<!-- RECOVER & HOW TO GET AN ACCOUNT -->
			<div class="sec_3">
				<a href="/auth/login">Back to Sign In</a>
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
				gap: 2.4rem;

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

				.email {
					width: 100%;
					height: 42px;
					margin-top: 3px;
					padding: 0.5rem;
					padding-right: 40px;
					box-sizing: border-box;
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
