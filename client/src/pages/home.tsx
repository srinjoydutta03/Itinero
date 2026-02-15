import { useState } from "react";
import { useLocation } from "wouter";
import { Layout } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { format } from "date-fns";
import { Calendar as CalendarIcon, MapPin, Users, Wallet, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import heroBg from "@/assets/hero-bg.jpg";
import { motion } from "framer-motion";

export default function Home() {
  const [_, setLocation] = useLocation();
  const [date, setDate] = useState<Date | undefined>(new Date());
  const [toDate, setToDate] = useState<Date | undefined>(undefined);
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app we would pass these params, but for mockup we just go to dashboard
    setLocation("/plan");
  };

  return (
    <Layout>
      <div className="relative min-h-[calc(100vh-64px)] w-full overflow-hidden">
        {/* Hero Background with Overlay */}
        <div 
          className="absolute inset-0 z-0 bg-cover bg-center bg-no-repeat"
          style={{ backgroundImage: `url(${heroBg})` }}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-black/20 to-background" />
        </div>

        <div className="container relative z-10 mx-auto flex min-h-[calc(100vh-64px)] flex-col items-center justify-center px-4 pb-20 pt-20 text-center sm:px-6">
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-8 max-w-3xl"
          >
            <h1 className="font-serif text-5xl font-medium leading-tight text-white drop-shadow-sm md:text-7xl">
              Curate your <span className="italic text-secondary">perfect</span> journey.
            </h1>
            <p className="mt-6 text-lg text-white/90 md:text-xl">
              AI-powered itineraries that adapt to your budget, style, and the weather.
            </p>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="w-full max-w-4xl"
          >
            <form onSubmit={handleSearch} className="grid grid-cols-1 gap-2 rounded-2xl bg-white/95 p-2 shadow-2xl backdrop-blur-sm lg:grid-cols-12 lg:items-center lg:gap-4 lg:p-3">
              
              {/* Origin Input */}
              <div className="col-span-1 lg:col-span-2">
                <div className="relative flex h-14 items-center rounded-xl bg-muted/50 px-4 transition-colors hover:bg-muted/80">
                  <MapPin className="mr-3 h-5 w-5 text-muted-foreground" />
                  <div className="flex w-full flex-col items-start text-left">
                    <Label htmlFor="origin" className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">From</Label>
                    <input 
                      id="origin" 
                      type="text" 
                      placeholder="New York" 
                      className="w-full bg-transparent text-sm font-medium text-foreground outline-none placeholder:text-muted-foreground/50"
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Destination Input */}
              <div className="col-span-1 lg:col-span-2">
                <div className="relative flex h-14 items-center rounded-xl bg-muted/50 px-4 transition-colors hover:bg-muted/80">
                  <MapPin className="mr-3 h-5 w-5 text-muted-foreground" />
                  <div className="flex w-full flex-col items-start text-left">
                    <Label htmlFor="destination" className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">To</Label>
                    <input 
                      id="destination" 
                      type="text" 
                      placeholder="Paris" 
                      className="w-full bg-transparent text-sm font-medium text-foreground outline-none placeholder:text-muted-foreground/50"
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Date Picker Group */}
              <div className="col-span-1 lg:col-span-3">
                <div className="flex gap-2">
                  <Popover>
                    <PopoverTrigger asChild>
                      <button type="button" className="relative flex h-14 w-full flex-1 items-center rounded-xl bg-muted/50 px-3 transition-colors hover:bg-muted/80 overflow-hidden">
                        <div className="flex w-full flex-col items-start text-left min-w-0">
                           <Label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground whitespace-nowrap">From</Label>
                           <span className={cn("text-sm font-medium truncate w-full", !date && "text-muted-foreground/50")}>
                             {date ? format(date, "MMM dd") : "Date"}
                           </span>
                        </div>
                      </button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar
                        mode="single"
                        selected={date}
                        onSelect={setDate}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>

                  <Popover>
                    <PopoverTrigger asChild>
                      <button type="button" className="relative flex h-14 w-full flex-1 items-center rounded-xl bg-muted/50 px-3 transition-colors hover:bg-muted/80 overflow-hidden">
                        <div className="flex w-full flex-col items-start text-left min-w-0">
                           <Label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground whitespace-nowrap">To</Label>
                           <span className={cn("text-sm font-medium truncate w-full", !toDate && "text-muted-foreground/50")}>
                             {toDate ? format(toDate, "MMM dd") : "Date"}
                           </span>
                        </div>
                      </button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar
                        mode="single"
                        selected={toDate}
                        onSelect={setToDate}
                        initialFocus
                        disabled={(date) => date < (new Date())}
                      />
                    </PopoverContent>
                  </Popover>
                </div>
              </div>

              {/* Travelers & Budget Group */}
              <div className="col-span-1 flex gap-2 lg:col-span-3">
                <div className="relative flex h-14 flex-1 items-center rounded-xl bg-muted/50 px-3 transition-colors hover:bg-muted/80">
                  <Users className="mr-2 h-4 w-4 text-muted-foreground" />
                  <div className="flex w-full flex-col items-start text-left">
                    <Label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Guests</Label>
                    <input type="number" min="1" placeholder="2" className="w-full bg-transparent text-sm font-medium outline-none" />
                  </div>
                </div>
                <div className="relative flex h-14 flex-1 items-center rounded-xl bg-muted/50 px-3 transition-colors hover:bg-muted/80">
                  <Wallet className="mr-2 h-4 w-4 text-muted-foreground" />
                  <div className="flex w-full flex-col items-start text-left">
                    <Label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Budget</Label>
                    <input type="number" placeholder="$2k" className="w-full bg-transparent text-sm font-medium outline-none" />
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <div className="col-span-1 lg:col-span-2">
                <Button type="submit" size="lg" className="h-14 w-full min-w-0 rounded-xl bg-primary px-2 text-base font-medium text-white shadow-lg transition-transform hover:scale-[1.02] hover:bg-primary/90 overflow-hidden whitespace-nowrap">
                  <span className="truncate">Start Planning</span>
                  <ArrowRight className="ml-2 h-5 w-5 flex-shrink-0" />
                </Button>
              </div>

            </form>
            
            <div className="mt-6 flex flex-wrap justify-center gap-4 text-sm font-medium text-white/80">
              <span className="flex items-center gap-1.5 rounded-full bg-white/10 px-3 py-1 backdrop-blur-md">
                <span>✨</span> AI Curated
              </span>
               <span className="flex items-center gap-1.5 rounded-full bg-white/10 px-3 py-1 backdrop-blur-md">
                <span>🌤️</span> Weather Aware
              </span>
               <span className="flex items-center gap-1.5 rounded-full bg-white/10 px-3 py-1 backdrop-blur-md">
                <span>💰</span> Budget Optimized
              </span>
            </div>
          </motion.div>
        </div>
      </div>
    </Layout>
  );
}
