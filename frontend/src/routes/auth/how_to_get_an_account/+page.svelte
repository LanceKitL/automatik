<script lang="ts">
	import logo from '$lib/assets/LOGO.png';
	import left from '$lib/assets/AUTH/DESIGN.png';
	import { ArrowLeft } from '@lucide/svelte';
</script>
<header>
	<title>How to get an Account</title>
</header>
<div class="container">
	<div class="left_side">
		<div class="bg">
			<img src={left} alt="background" class="img_bg" width="500">
		</div>
	</div>

	<div class="right_side">
		<div class="r_container">
			<div class="sec_1">
				<div class="heading">
					<img src={logo} alt="Logo" width="300">
					<h1>How to Get an Account</h1>
					<span class="subtitle">Access to this system is controlled by the company. Public self-registration is not available.</span>
				</div>
			</div>

			<div class="sections">
				<div class="section">
					<h2>Customers</h2>
					<p style="text-align: justify;">Customer accounts are created during the vehicle purchase process. When a customer purchases a vehicle, an authorized company representative (Administrator or Agent) creates the customer's account on their behalf. The customer will then receive a temporary password that can be used to log in to the system.</p>
				</div>

				<div class="section">
					<h2>Company Staff</h2>
					<p>The following accounts are managed internally by the company:</p>
					<ul>
						<li>Agent</li>
						<li>Finance Staff</li>
						<li>Service Staff</li>
					</ul>
					<p>These accounts cannot be self-registered. They are created by an Administrator based on the employee's role and responsibilities.</p>
				</div>

				<div class="section need-help">
					<h2>Need an account?</h2>
					<p>Customers should contact their sales representative or company office. Employees should contact their company administrator or supervisor for account access.</p>
				</div>
			</div>

			<div class="back-link">
				<a href="/auth/login">
					<ArrowLeft size={14} />
					Back to Login
				</a>
			</div>
		</div>
	</div>
</div>

<style>
	.container {
		display: flex;
		justify-content: space-around;
		padding: 5rem 3rem;
	}

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
			width: 460px;
			display: flex;
			flex-direction: column;
			justify-content: center;
			padding-left: 4rem;
			padding-top: 3rem;
			gap: 1.5rem;
		}
	}

	.heading {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		text-align: center;
		gap: 0.5rem;

		img {
			margin-bottom: 0.5rem;
		}

		h1 {
			font-size: 22px;
			font-weight: 700;
			color: #1a1a2e;
			margin: 0;
		}

		.subtitle {
			font-size: 13px;
			color: #6b7280;
			max-width: 360px;
			line-height: 1.5;
		}
	}

	.sections {
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
	}

	.section {
		h2 {
			font-size: 15px;
			font-weight: 700;
			color: #1a1a2e;
			margin: 0 0 6px 0;
		}

		p {
			font-size: 13px;
			color: #6b7280;
			line-height: 1.6;
			margin: 0 0 6px 0;
		}

		ul {
			margin: 4px 0 10px 0;
			padding-left: 1.25rem;

			li {
				font-size: 13px;
				color: #374151;
				line-height: 1.7;
			}
		}

		&.need-help {
			padding: 1rem 1rem;
			border-radius: 1rem;
			background-color: rgb(255, 255, 194);
			margin-top: auto;
			padding-top: 0.75rem;

			h2 {
				color: #71733f;
			}

			p {
				color: #71733f;
			}
		}
	}

	.back-link {
		margin-top: 0.5rem;

		a {
			display: inline-flex;
			align-items: center;
			gap: 6px;
			font-size: 13px;
			color: #0d76ff;
			text-decoration: none;
			font-weight: 500;

			&:hover {
				text-decoration: underline;
			}
		}
	}

	@media (max-width: 1100px) {
		.container {
			padding: 3rem 1.5rem;
		}

		.left_side {
			display: none;
		}

		.right_side {
			padding-right: 0;
			display: flex;
			justify-content: center;

			.r_container {
				padding-left: 0;
				width: 100%;
				max-width: 460px;
			}
		}
	}
</style>
