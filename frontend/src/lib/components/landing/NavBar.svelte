<script lang="ts">
  import { Bell, Menu, X, Car } from "lucide-svelte";
  import { Button } from "$lib/components/ui/button";

  let open = false;

  const links = [
    { label: "Home", href: "#home" },
    { label: "Browse Vehicles", href: "#featured" },
    { label: "Loan Calculator", href: "#why" },
    { label: "Contact", href: "#footer" },
    { label: "About", href: "#why" }
  ];
</script>

<header
  class="sticky top-0 z-50 w-full border-b border-border bg-background/85 backdrop-blur-md"
>
  <div
    class="mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-4 lg:px-8"
  >
    <a href="#home" class="flex items-center gap-2">
      <span
        class="grid h-9 w-9 place-items-center rounded-md bg-primary text-primary-foreground"
      >
        <Car class="h-5 w-5" />
      </span>
      <span
        class="font-sans text-xl font-bold tracking-tight text-text-primary"
      >
        Automatik
      </span>
    </a>

    <nav class="hidden items-center gap-8 lg:flex">
      {#each links as link}
        <a
          href={link.href}
          class="text-sm font-medium text-text-light transition-colors hover:text-primary"
        >
          {link.label}
        </a>
      {/each}
    </nav>

    <div class="flex items-center gap-2">
      <button
        class="relative hidden h-10 w-10 items-center justify-center rounded-md text-text-light transition-colors hover:bg-secondary hover:text-primary lg:flex"
        aria-label="Notifications"
      >
        <Bell class="h-5 w-5" />
        <span
          class="absolute right-2 top-2 h-2 w-2 rounded-full bg-accent-dark"
        />
      </button>

      <Button
        class="hidden bg-primary text-primary-foreground hover:bg-primary-dark lg:inline-flex"
      >
        Login
      </Button>

      <button
        on:click={() => (open = !open)}
        class="grid h-10 w-10 place-items-center rounded-md text-text-primary lg:hidden"
        aria-label="Toggle menu"
      >
        {#if open}
          <X class="h-5 w-5" />
        {:else}
          <Menu class="h-5 w-5" />
        {/if}
      </button>
    </div>
  </div>

  {#if open}
    <div class="border-t border-border bg-background lg:hidden">
      <div class="mx-auto flex max-w-7xl flex-col gap-1 px-4 py-3">
        {#each links as link}
          <a
            href={link.href}
            on:click={() => (open = false)}
            class="rounded-md px-3 py-2 text-sm font-medium text-text-primary hover:bg-secondary"
          >
            {link.label}
          </a>
        {/each}

        <Button
          class="mt-2 w-full bg-primary text-primary-foreground hover:bg-primary-dark"
        >
          Login
        </Button>
      </div>
    </div>
  {/if}
</header>