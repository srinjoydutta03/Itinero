import { Link, useLocation } from "wouter";
import { cn } from "@/lib/utils";
import { Search, Map, User, Menu } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Layout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();

  return (
    <div className="min-h-screen bg-background font-sans text-foreground selection:bg-primary/20">
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-background/80 backdrop-blur-md">
        <div className="container mx-auto flex h-16 items-center justify-between px-4 sm:px-6">
          <Link href="/">
            <a className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-white">
                <Map className="h-5 w-5" />
              </div>
              <span className="font-serif text-xl font-semibold tracking-tight text-primary">Itinero</span>
            </a>
          </Link>

          <div className="hidden items-center gap-6 md:flex">
            <Link href="/">
              <a className={cn("text-sm font-medium transition-colors hover:text-primary", location === "/" ? "text-primary" : "text-muted-foreground")}>
                Plan Trip
              </a>
            </Link>
            <Link href="/saved">
              <a className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
                Saved Itineraries
              </a>
            </Link>
            <Link href="/explore">
              <a className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
                Explore
              </a>
            </Link>
          </div>

          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-primary">
              <Search className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon" className="hidden text-muted-foreground hover:text-primary sm:flex">
              <User className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon" className="md:hidden">
              <Menu className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </nav>

      <main className="pt-16">
        {children}
      </main>
    </div>
  );
}
