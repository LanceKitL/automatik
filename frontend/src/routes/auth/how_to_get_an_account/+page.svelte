<script lang="ts">
    import logo from '$lib/assets/LOGO.png'
    import {ArrowBigLeft} from '@lucide/svelte'
</script>
<div class="contain">
	<div class="column">
		<div class="row-view">
			<img
				src={ArrowBigLeft}
                alt="arrow"
				class="image"
			/>
			<span class="text" >
				back to login
			</span>
			<img
				src={logo}
                alt="logo"
				class="image2"
			/>
		</div>
		<div class="box">
		</div>
		<div class="column2">
			<span class="text2" >
				Access to this system is controlled by the company. Public self-registration is not available. Accounts are created and managed according to the user's role.
			</span>
			<div class="column3">
				<span class="text3" >
					How Customers Get Their Account
				</span>
				<span class="text4" >
					Customer accounts are created during the vehicle purchase process.
				</span>
				<span class="text5" >
					When a customer purchases a vehicle, an authorized company representative (Administrator or Agent) creates the customer's account on their behalf. The customer will then receive a temporary password that can be used to log in to the system.
				</span>
			</div>
			<div class="column4">
				<span class="text3" >
					How Company Staff Get Their Account
				</span>
				<span class="text4" >
					The following accounts are managed internally by the company:
				</span>
				<span class="text6" >
					Agent\nFinance Staff\nService Staff
				</span>
				<span class="text5" >
					These accounts cannot be self-registered. They are created by an Administrator based on the employee's role and responsibilities.
				</span>
			</div>
		</div>
		<button class="button"
			onclick={() => alert('Pressed!')}>
			<div class="column5">
				<span class="text7" >
					Need an account?
				</span>
				<span class="text8" >
					Customers should contact their sales representative or company office. Employees should contact their company administrator or supervisor for account access.
				</span>
			</div>
		</button>
	</div>
</div>
<style>
	.box {
		max-width: 1400px;
		height: 1px;
		align-self: stretch;
		background: #A1A1A1;
		margin-bottom: 70px;
		margin-left: auto;
		margin-right: auto;
	}
	.button {
		max-width: 1400px;
		align-self: stretch;
		display: flex;
		flex-direction: column;
		align-items: center;
		background: #FFFDD633;
		border-radius: 40px;
		border: none;
		padding-top: 49px;
		padding-bottom: 49px;
		margin-left: auto;
		margin-right: auto;
		text-align: left;
	}
	.column {
		align-self: stretch;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		background: #FFFFFF;
		padding-top: 84px;
		padding-bottom: 84px;
		box-shadow: 0px 4px 4px #00000040;
	}
	.column2 {
		max-width: 1354px;
		align-self: stretch;
		display: flex;
		flex-direction: column;
		margin-bottom: 124px;
		margin-left: auto;
		margin-right: auto;
	}
	.column3 {
		align-self: stretch;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		margin-bottom: 143px;
	}
	.column4 {
		align-self: stretch;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		margin-right: 27px;
	}
	.column5 {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		padding-right: 12px;
		gap: 22px;
	}
	.contain {
		display: flex;
		flex-direction: column;
		background: #FFFFFF;
	}
	.image {
		width: 47px;
		height: 47px;
		margin-right: 4px;
		object-fit: fill;
	}
	.image2 {
		width: 567px;
		height: 173px;
		margin-top: 38px;
		object-fit: fill;
	}
	.row-view {
		display: flex;
		align-items: flex-start;
		margin-bottom: 53px;
		margin-left: 79px;
	}
	.text {
		color: #2364C5;
		font-size: 22px;
		font-weight: bold;
		margin-top: 9px;
		margin-right: 405px;
	}
	.text2 {
		color: #000000;
		font-size: 30px;
		margin-bottom: 134px;
	}
	.text3 {
		color: #000000;
		font-size: 48px;
		font-weight: bold;
		margin-bottom: 23px;
	}
	.text4 {
		color: #7F7F7F;
		font-size: 30px;
		margin-bottom: 33px;
	}
	.text5 {
		color: #000000;
		font-size: 30px;
	}
	.text6 {
		color: #000000;
		font-size: 30px;
		margin-bottom: 33px;
		width: 214px;
	}
	.text7 {
		color: #BABC72;
		font-size: 48px;
		font-weight: bold;
		margin-right: 760px;
	}
	.text8 {
		color: #BABC72;
		font-size: 30px;
		width: 1172px;
	}
</style>