import { useState, useEffect } from "react";
import { Layout } from "@/components/layout";
import { generateMockItinerary, type Itinerary } from "@/lib/mockData";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  CloudSun, 
  Plane, 
  Train, 
  Star,
  MessageSquare, 
  Send
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

export default function Dashboard() {
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeDay, setActiveDay] = useState(1);
  const [chatOpen, setChatOpen] = useState(true);

  useEffect(() => {
    // Simulate AI loading
    const timer = setTimeout(() => {
      setItinerary(generateMockItinerary({
        destination: "Paris",
        dates: { from: new Date(), to: new Date() },
        travelers: 2,
        budget: 5000
      }));
      setLoading(false);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <Layout>
        <div className="flex h-[80vh] w-full flex-col items-center justify-center gap-6">
          <div className="relative flex h-20 w-20 items-center justify-center">
            <div className="absolute inset-0 animate-ping rounded-full bg-primary/20"></div>
            <Plane className="h-10 w-10 animate-bounce text-primary" />
          </div>
          <div className="text-center">
            <h2 className="text-2xl font-serif font-medium text-foreground">Curating your Parisian experience...</h2>
            <p className="mt-2 text-muted-foreground">Checking weather forecasts, finding hidden gems, and optimizing costs.</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!itinerary) return null;

  return (
    <Layout>
      <div className="relative flex h-[calc(100vh-64px)] overflow-hidden">
        
        {/* Main Content Area - Scrollable */}
        <div className="flex-1 overflow-y-auto bg-muted/10 p-4 pb-20 sm:p-6 lg:p-8">
          <div className="mx-auto max-w-5xl space-y-8">
            
            {/* Header / Overview */}
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid gap-6 md:grid-cols-12"
            >
              <div className="md:col-span-8">
                <div className="flex items-end justify-between">
                  <div>
                    <h1 className="font-serif text-4xl font-medium text-foreground">Trip to {itinerary.destination}</h1>
                    <p className="mt-2 text-muted-foreground flex items-center gap-2">
                      <CloudSun className="h-4 w-4" />
                      {itinerary.weatherSummary}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="md:col-span-4">
                <Card className="border-none bg-primary/5 shadow-sm">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between text-sm font-medium">
                      <span className="text-muted-foreground">Total Budget</span>
                      <span className="font-bold text-foreground">$5,000</span>
                    </div>
                    <div className="mt-3">
                      <div className="flex items-end justify-between mb-1">
                        <span className="text-xs text-muted-foreground">Estimated Cost</span>
                        <span className="font-bold text-primary">${itinerary.totalCost}</span>
                      </div>
                      <Progress value={(itinerary.totalCost / 5000) * 100} className="h-2 bg-white" />
                      <p className="mt-2 text-xs text-right text-emerald-600 font-medium">
                        ${itinerary.remainingBudget} remaining
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </motion.div>

            <Tabs defaultValue="itinerary" className="w-full">
              <TabsList className="w-full justify-start rounded-xl border bg-background p-1 shadow-sm overflow-x-auto">
                <TabsTrigger value="itinerary" className="rounded-lg px-6">Itinerary</TabsTrigger>
                <TabsTrigger value="transport" className="rounded-lg px-6">Transport</TabsTrigger>
                <TabsTrigger value="hotels" className="rounded-lg px-6">Hotels</TabsTrigger>
                <TabsTrigger value="food" className="rounded-lg px-6">Dining</TabsTrigger>
              </TabsList>
              
              <div className="mt-6">
                <TabsContent value="itinerary" className="space-y-6">
                  {/* Timeline Days */}
                  <div className="flex items-center gap-4 overflow-x-auto pb-4 no-scrollbar">
                    {itinerary.days.map((day) => (
                      <button
                        key={day.day}
                        onClick={() => setActiveDay(day.day)}
                        className={cn(
                          "flex min-w-[100px] flex-col items-center justify-center rounded-xl border p-4 transition-all hover:border-primary/50 hover:shadow-md",
                          activeDay === day.day 
                            ? "border-primary bg-primary text-white shadow-lg scale-105" 
                            : "border-border bg-card text-foreground"
                        )}
                      >
                        <span className="text-xs font-medium uppercase tracking-wide opacity-80">{day.date}</span>
                        <span className="text-2xl font-serif font-bold">Day {day.day}</span>
                        <span className="mt-1 text-xs opacity-80 capitalize">{day.weather.condition}</span>
                      </button>
                    ))}
                  </div>

                  {/* Day Content */}
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={activeDay}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-4"
                    >
                      {itinerary.days.find(d => d.day === activeDay)?.activities.map((activity, idx) => (
                        <div key={activity.id} className="group relative flex gap-6 rounded-2xl border bg-card p-4 transition-all hover:shadow-md">
                          {/* Timeline Line */}
                          {idx !== itinerary.days.find(d => d.day === activeDay)?.activities.length! - 1 && (
                            <div className="absolute left-[3.25rem] top-16 h-[calc(100%+1rem)] w-[2px] bg-border group-hover:bg-primary/20"></div>
                          )}
                          
                          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full border bg-background shadow-sm text-xs font-bold text-muted-foreground z-10">
                            {activity.time.split(' ')[0]}
                          </div>

                          <div className="flex flex-1 flex-col gap-4 sm:flex-row">
                             <div className="h-32 w-full shrink-0 overflow-hidden rounded-xl sm:w-48">
                               <img src={activity.image} alt={activity.name} className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110" />
                             </div>
                             <div className="flex flex-1 flex-col justify-between py-1">
                               <div>
                                 <div className="flex items-start justify-between">
                                   <h3 className="text-lg font-semibold text-foreground">{activity.name}</h3>
                                   <Badge variant="secondary" className="capitalize">{activity.type}</Badge>
                                 </div>
                                 <p className="mt-1 text-sm text-muted-foreground line-clamp-2">{activity.description}</p>
                               </div>
                               
                               <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
                                 {activity.cost > 0 ? (
                                   <span className="flex items-center gap-1 font-medium text-foreground">
                                     <span className="text-primary font-bold">${activity.cost}</span> est.
                                   </span>
                                 ) : (
                                   <span className="flex items-center gap-1 font-medium text-emerald-600">Free</span>
                                 )}
                                 {activity.rating > 0 && (
                                   <span className="flex items-center gap-1">
                                     <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                                     {activity.rating}
                                   </span>
                                 )}
                               </div>
                             </div>
                          </div>
                        </div>
                      ))}
                    </motion.div>
                  </AnimatePresence>
                </TabsContent>

                <TabsContent value="transport">
                   <div className="grid gap-4 sm:grid-cols-2">
                      {itinerary.transport.map((opt, i) => (
                        <Card key={i} className="overflow-hidden transition-all hover:shadow-md hover:border-primary/50">
                          <CardContent className="p-0">
                            <div className="flex items-center justify-between bg-muted/30 p-4">
                              <div className="flex items-center gap-3">
                                <div className="rounded-lg bg-background p-2 shadow-sm">
                                  {opt.type === 'flight' ? <Plane className="h-5 w-5 text-primary" /> : <Train className="h-5 w-5 text-primary" />}
                                </div>
                                <div>
                                  <h3 className="font-semibold">{opt.provider}</h3>
                                  <p className="text-xs text-muted-foreground capitalize">{opt.type}</p>
                                </div>
                              </div>
                              <div className="text-right">
                                <span className="block text-lg font-bold text-foreground">${opt.totalPrice}</span>
                                <span className="text-xs text-muted-foreground">For all travelers</span>
                              </div>
                            </div>
                            <div className="grid grid-cols-3 gap-4 p-4 text-center">
                              <div>
                                <span className="block text-lg font-medium">{opt.departure}</span>
                                <span className="text-xs text-muted-foreground">Departure</span>
                              </div>
                              <div className="flex flex-col items-center justify-center">
                                <span className="text-xs text-muted-foreground mb-1">{opt.duration}</span>
                                <div className="h-[2px] w-full bg-border relative">
                                  <div className="absolute right-0 -top-1 h-2 w-2 rounded-full bg-border"></div>
                                  <div className="absolute left-0 -top-1 h-2 w-2 rounded-full bg-primary"></div>
                                </div>
                              </div>
                              <div>
                                <span className="block text-lg font-medium">{opt.arrival}</span>
                                <span className="text-xs text-muted-foreground">Arrival</span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                   </div>
                </TabsContent>
                
                <TabsContent value="hotels">
                  <div className="grid gap-6 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                    {itinerary.hotels.map((hotel) => (
                      <Card key={hotel.id} className="group overflow-hidden">
                        <div className="relative h-48 w-full overflow-hidden">
                           <img src={hotel.image} alt={hotel.name} className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110" />
                           <div className="absolute top-3 right-3 rounded-full bg-background/90 px-2 py-1 text-xs font-bold shadow-sm backdrop-blur-sm">
                             ${hotel.pricePerNight}/night
                           </div>
                        </div>
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between">
                            <h3 className="font-serif text-lg font-semibold">{hotel.name}</h3>
                            <div className="flex items-center gap-1 text-sm font-medium">
                              <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                              {hotel.rating}
                            </div>
                          </div>
                          <div className="mt-3 flex flex-wrap gap-2">
                            {hotel.amenities.map(a => (
                              <Badge key={a} variant="outline" className="bg-muted/50 font-normal">{a}</Badge>
                            ))}
                          </div>
                          <Button className="mt-4 w-full" variant="outline">View Details</Button>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>

                 <TabsContent value="food">
                  <div className="grid gap-6 sm:grid-cols-2">
                    {itinerary.restaurants.map((rest) => (
                      <Card key={rest.id} className="flex flex-row overflow-hidden transition-all hover:shadow-md">
                        <div className="w-1/3 shrink-0">
                          <img src={rest.image} alt={rest.name} className="h-full w-full object-cover" />
                        </div>
                        <CardContent className="flex flex-1 flex-col justify-between p-4">
                          <div>
                            <h3 className="font-serif text-lg font-semibold">{rest.name}</h3>
                            <p className="text-sm text-muted-foreground line-clamp-2 mt-1">{rest.description}</p>
                          </div>
                          <div className="mt-3 flex items-center justify-between">
                             <div className="flex items-center gap-1 text-sm font-medium">
                              <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                              {rest.rating}
                            </div>
                            <span className="text-sm font-bold text-primary">${rest.cost} est.</span>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>
              </div>
            </Tabs>

          </div>
        </div>

        {/* AI Chat Sidebar */}
        <div className={cn(
          "fixed inset-y-0 right-0 z-50 w-80 transform border-l bg-background shadow-2xl transition-transform duration-300 ease-in-out md:relative md:translate-x-0 md:shadow-none",
          chatOpen ? "translate-x-0" : "translate-x-full md:hidden"
        )}>
           <div className="flex h-full flex-col">
             <div className="flex items-center justify-between border-b p-4">
               <div className="flex items-center gap-2">
                 <div className="rounded-full bg-primary/10 p-1.5">
                   <MessageSquare className="h-4 w-4 text-primary" />
                 </div>
                 <h3 className="font-semibold">Trip Assistant</h3>
               </div>
               <Button variant="ghost" size="icon" onClick={() => setChatOpen(false)} className="md:hidden">
                 <span className="sr-only">Close</span>
                 <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg" className="h-4 w-4"><path d="M11.7816 4.03157C12.0062 3.80702 12.0062 3.44295 11.7816 3.2184C11.5571 2.99385 11.193 2.99385 10.9685 3.2184L7.50005 6.68682L4.03164 3.2184C3.80708 2.99385 3.44301 2.99385 3.21846 3.2184C2.99391 3.44295 2.99391 3.80702 3.21846 4.03157L6.68688 7.49999L3.21846 10.9684C2.99391 11.193 2.99391 11.557 3.21846 11.7816C3.44301 12.0061 3.80708 12.0061 4.03164 11.7816L7.50005 8.31316L10.9685 11.7816C11.193 12.0061 11.5571 12.0061 11.7816 11.7816C12.0062 11.557 12.0062 11.193 11.7816 10.9684L8.31322 7.49999L11.7816 4.03157Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path></svg>
               </Button>
             </div>
             
             <ScrollArea className="flex-1 p-4">
               <div className="space-y-4">
                 <div className="flex gap-3">
                   <div className="h-8 w-8 shrink-0 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary">AI</div>
                   <div className="rounded-2xl rounded-tl-none bg-muted px-4 py-3 text-sm">
                     Hi! I've drafted a 3-day itinerary for Paris. Would you like to add more museum visits or focus on food tours?
                   </div>
                 </div>
                 <div className="flex flex-row-reverse gap-3">
                   <div className="h-8 w-8 shrink-0 rounded-full bg-primary flex items-center justify-center text-xs font-bold text-white">Me</div>
                   <div className="rounded-2xl rounded-tr-none bg-primary text-white px-4 py-3 text-sm shadow-sm">
                     Looks great! Can we find a cheaper hotel option? Maybe around $150/night?
                   </div>
                 </div>
                  <div className="flex gap-3">
                   <div className="h-8 w-8 shrink-0 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary">AI</div>
                   <div className="rounded-2xl rounded-tl-none bg-muted px-4 py-3 text-sm">
                     I found "Modern Loft Stay" which is $180/night. It's slightly above but very central. I've updated the list!
                   </div>
                 </div>
               </div>
             </ScrollArea>
             
             <div className="border-t p-4">
               <div className="relative">
                 <input 
                   type="text" 
                   placeholder="Ask for changes..." 
                   className="w-full rounded-full border bg-background pl-4 pr-10 py-3 text-sm shadow-sm outline-none focus:ring-1 focus:ring-primary"
                 />
                 <Button size="icon" className="absolute right-1 top-1 h-8 w-8 rounded-full">
                   <Send className="h-4 w-4" />
                 </Button>
               </div>
             </div>
           </div>
        </div>
        
        {/* Chat Toggle Button for Mobile/Desktop when closed */}
        {!chatOpen && (
           <Button 
             className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-xl z-50"
             onClick={() => setChatOpen(true)}
           >
             <MessageSquare className="h-6 w-6" />
           </Button>
        )}
      </div>
    </Layout>
  );
}
