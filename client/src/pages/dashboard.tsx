import { useState, useEffect, useRef, useCallback } from "react";
import { useSearch } from "wouter";
import { Layout } from "@/components/layout";
import { createPlan, sendChatMessage } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import type {
  TravelPlanResponse,
  Attraction,
  HiddenGem,
  ChatResponse,
} from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  CloudSun,
  Plane,
  Star,
  MessageSquare,
  Send,
  Sparkles,
  AlertCircle,
  Hotel,
  MapPin,
  DollarSign,
  Calendar,
  Thermometer,
  Droplets,
  ChevronDown,
  ChevronUp,
  Utensils,
  Gem,
  Sun,
  Moon,
  Coffee,
  ClipboardList,
} from "lucide-react";
import { motion } from "framer-motion";
import Markdown from "react-markdown";
import { cn } from "@/lib/utils";
import { Toaster } from "@/components/ui/toaster";

interface ChatMsg {
  role: "user" | "assistant";
  content: string;
}

export default function Dashboard() {
  const searchString = useSearch();
  const params = new URLSearchParams(searchString);

  const origin = params.get("origin") || "New York";
  const destination = params.get("destination") || "Paris";
  const startDate = params.get("startDate") || "";
  const endDate = params.get("endDate") || "";
  const travelers = Number(params.get("travelers") || "2");
  const budget = Number(params.get("budget") || "3000");
  const travelStyle = (params.get("travelStyle") || "standard") as "affordable" | "standard" | "premium" | "luxury";

  const [plan, setPlan] = useState<TravelPlanResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summaryExpanded, setSummaryExpanded] = useState(false);

  const [chatOpen, setChatOpen] = useState(true);
  const [chatSessionId, setChatSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const [selectedAttraction, setSelectedAttraction] = useState<Attraction | null>(null);
  const [selectedGem, setSelectedGem] = useState<HiddenGem | null>(null);
  const [planVersion, setPlanVersion] = useState(0);
  const { toast } = useToast();

  // ── Fetch travel plan on mount ────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;

    async function fetchPlan() {
      if (!startDate || !endDate || !destination) {
        setError("Missing trip details — please go back and fill in all fields.");
        setLoading(false);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const response = await createPlan({
          destination,
          start_date: startDate,
          end_date: endDate,
          budget_usd: budget,
          origin,
          travel_style: travelStyle,
          preferences: [],
          dislikes: [],
        });
        if (!cancelled) {
          setPlan(response);
          setChatSessionId(response.session_id);
          if (response.llm_summary) {
            setMessages([{ role: "assistant", content: response.llm_summary }]);
          } else {
            setMessages([
              {
                role: "assistant",
                content: `I've drafted your trip to ${response.destination}! Feel free to ask me to adjust anything.`,
              },
            ]);
          }
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.message || "Unknown error");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchPlan();
    return () => { cancelled = true; };
  }, [destination, startDate, endDate, budget, origin, travelStyle]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendChat = useCallback(async () => {
    const text = chatInput.trim();
    if (!text || chatLoading) return;
    setChatInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setChatLoading(true);
    try {
      const res: ChatResponse = await sendChatMessage({
        session_id: chatSessionId,
        message: text,
      });
      setChatSessionId(res.session_id);
      setMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);

      // If the chat turn triggered agent updates, refresh the plan data
      if (res.updated_plan) {
        setPlan(res.updated_plan);
        setPlanVersion((v) => v + 1);
        toast({
          title: "✨ Plan Updated",
          description: "Your itinerary and trip details have been refreshed based on your request.",
        });
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Sorry, something went wrong: ${err.message}` },
      ]);
    } finally {
      setChatLoading(false);
    }
  }, [chatInput, chatLoading, chatSessionId]);

  // ── Loading ───────────────────────────────────────────────────────────
  if (loading) {
    return (
      <Layout>
        <div className="flex h-[80vh] w-full flex-col items-center justify-center gap-6">
          <div className="relative flex h-20 w-20 items-center justify-center">
            <div className="absolute inset-0 animate-ping rounded-full bg-primary/20" />
            <Plane className="h-10 w-10 animate-bounce text-primary" />
          </div>
          <div className="text-center">
            <h2 className="text-2xl font-serif font-medium">Curating your {destination} experience...</h2>
            <p className="mt-2 text-muted-foreground">Checking weather, searching flights & hotels, finding hidden gems.</p>
            <p className="mt-1 text-xs text-muted-foreground">This may take 1–3 minutes while our AI agents work.</p>
          </div>
        </div>
      </Layout>
    );
  }

  // ── Error ─────────────────────────────────────────────────────────────
  if (error) {
    return (
      <Layout>
        <div className="flex h-[80vh] w-full flex-col items-center justify-center gap-6">
          <AlertCircle className="h-16 w-16 text-destructive" />
          <div className="text-center max-w-lg">
            <h2 className="text-2xl font-serif font-medium">Something went wrong</h2>
            <div className="mt-4 rounded-lg border border-destructive/20 bg-destructive/5 p-4 text-left">
              <p className="text-sm font-mono text-destructive break-all whitespace-pre-wrap">{error}</p>
            </div>
            <p className="mt-4 text-sm text-muted-foreground">Make sure the FastAPI backend is running on port 8000.</p>
            <Button className="mt-6" onClick={() => window.location.reload()}>Try Again</Button>
          </div>
        </div>
      </Layout>
    );
  }

  if (!plan) return null;

  const totalCost = plan.budget.estimated_total_usd;
  const remaining = plan.budget.remaining_budget_usd;
  const breakdown = plan.budget.breakdown;
  const summaryText = plan.llm_summary || "";
  const summaryPreview = summaryText.length > 600 ? summaryText.slice(0, 600) + "..." : summaryText;

  return (
    <Layout>
      <div className="relative flex h-[calc(100vh-64px)] overflow-hidden">
        {/* Main Content */}
        <div className="flex-1 overflow-y-auto bg-muted/10 p-4 pb-20 sm:p-6 lg:p-8">
          <div className="mx-auto max-w-5xl space-y-8">

            {/* Header */}
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
              <div className="flex items-end justify-between flex-wrap gap-4">
                <div>
                  <h1 className="font-serif text-4xl font-medium">Trip to {plan.destination}</h1>
                  <p className="mt-2 text-muted-foreground flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    {plan.dates.start_date} → {plan.dates.end_date} · {plan.dates.num_days} days
                  </p>
                </div>
                <div className="flex gap-2 flex-wrap">
                  {plan.agents_run.map((a) => (
                    <Badge key={a} variant="secondary" className="capitalize">✓ {a}</Badge>
                  ))}
                </div>
              </div>

              {/* Cost breakdown cards */}
              <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
                <Card className="border-none bg-blue-50 dark:bg-blue-950/30">
                  <CardContent className="p-4 text-center">
                    <Plane className="h-5 w-5 mx-auto text-blue-600 mb-1" />
                    <p className="text-xs text-muted-foreground">Transport</p>
                    <p className="text-lg font-bold">${breakdown.transport_usd.toLocaleString()}</p>
                  </CardContent>
                </Card>
                <Card className="border-none bg-purple-50 dark:bg-purple-950/30">
                  <CardContent className="p-4 text-center">
                    <Hotel className="h-5 w-5 mx-auto text-purple-600 mb-1" />
                    <p className="text-xs text-muted-foreground">Hotels</p>
                    <p className="text-lg font-bold">${breakdown.hotel_usd.toLocaleString()}</p>
                  </CardContent>
                </Card>
                <Card className="border-none bg-orange-50 dark:bg-orange-950/30">
                  <CardContent className="p-4 text-center">
                    <span className="text-xl block mb-1">🍽️</span>
                    <p className="text-xs text-muted-foreground">Food</p>
                    <p className="text-lg font-bold">${breakdown.food_usd.toLocaleString()}</p>
                  </CardContent>
                </Card>
                <Card className="border-none bg-green-50 dark:bg-green-950/30">
                  <CardContent className="p-4 text-center">
                    <MapPin className="h-5 w-5 mx-auto text-green-600 mb-1" />
                    <p className="text-xs text-muted-foreground">Activities</p>
                    <p className="text-lg font-bold">${breakdown.activities_usd.toLocaleString()}</p>
                  </CardContent>
                </Card>
              </div>

              {/* Budget progress */}
              <Card className="border-none bg-primary/5 shadow-sm">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between text-sm font-medium">
                    <span className="text-muted-foreground">Total Budget: ${budget.toLocaleString()}</span>
                    <span className="font-bold text-primary">Est. ${totalCost.toLocaleString()}</span>
                  </div>
                  <Progress value={Math.min((totalCost / budget) * 100, 100)} className="mt-2 h-2 bg-white" />
                  <p className={cn("mt-2 text-xs text-right font-medium", remaining >= 0 ? "text-emerald-600" : "text-destructive")}>
                    {remaining >= 0 ? `$${remaining.toLocaleString()} remaining` : `$${Math.abs(remaining).toLocaleString()} over budget`}
                  </p>
                </CardContent>
              </Card>
            </motion.div>

            {/* AI Summary */}
            {summaryText && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="rounded-full bg-primary/10 p-1.5">
                        <Sparkles className="h-4 w-4 text-primary" />
                      </div>
                      <h3 className="font-serif text-lg font-semibold">AI Travel Summary</h3>
                    </div>
                    <div className="prose prose-sm dark:prose-invert max-w-none text-foreground/90 leading-relaxed">
                      <Markdown>{summaryExpanded || summaryText.length <= 600 ? summaryText : summaryPreview}</Markdown>
                    </div>
                    {summaryText.length > 600 && (
                      <Button variant="ghost" size="sm" className="mt-3 text-primary" onClick={() => setSummaryExpanded(!summaryExpanded)}>
                        {summaryExpanded ? (<><ChevronUp className="h-4 w-4 mr-1" /> Show less</>) : (<><ChevronDown className="h-4 w-4 mr-1" /> Read full summary</>)}
                      </Button>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {/* Budget Suggestions */}
            {plan.budget.suggestions.length > 0 && (
              <Card className="border-primary/20 bg-primary/5">
                <CardContent className="p-4">
                  <h3 className="text-sm font-semibold flex items-center gap-2 mb-2">
                    <DollarSign className="h-4 w-4 text-primary" /> Budget Tips
                  </h3>
                  <ul className="space-y-1">
                    {plan.budget.suggestions.map((s, i) => (
                      <li key={i} className="text-sm text-muted-foreground">• {s}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* Errors */}
            {plan.errors.length > 0 && (
              <Card className="border-destructive/30 bg-destructive/5">
                <CardContent className="p-4">
                  <h3 className="text-sm font-semibold flex items-center gap-2 mb-2 text-destructive">
                    <AlertCircle className="h-4 w-4" /> Warnings
                  </h3>
                  <ul className="space-y-1">
                    {plan.errors.map((e, i) => (<li key={i} className="text-sm text-destructive/80">{e}</li>))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* Tabs */}
            <Tabs defaultValue="itinerary" className="w-full" key={`plan-tabs-${planVersion}`}>
              <TabsList className="w-full justify-start rounded-xl border bg-background p-1 shadow-sm overflow-x-auto">
                <TabsTrigger value="itinerary" className="rounded-lg px-5"><ClipboardList className="h-4 w-4 mr-1.5" />Itinerary</TabsTrigger>
                <TabsTrigger value="weather" className="rounded-lg px-5"><CloudSun className="h-4 w-4 mr-1.5" />Weather</TabsTrigger>
                <TabsTrigger value="transport" className="rounded-lg px-5"><Plane className="h-4 w-4 mr-1.5" />Flights</TabsTrigger>
                <TabsTrigger value="hotels" className="rounded-lg px-5"><Hotel className="h-4 w-4 mr-1.5" />Hotels</TabsTrigger>
                <TabsTrigger value="discoveries" className="rounded-lg px-5"><MapPin className="h-4 w-4 mr-1.5" />Discoveries</TabsTrigger>
              </TabsList>

              <div className="mt-6">

                {/* ── Itinerary ── */}
                <TabsContent value="itinerary" className="space-y-6">
                  {(() => {
                    const numDays = plan.dates.num_days;
                    const startDate = new Date(plan.dates.start_date + "T00:00:00");
                    const recFlight = plan.transport.recommended;
                    const recHotel = plan.hotel.recommended;
                    const attractions = plan.discovery.attractions;
                    const restaurants = plan.discovery.restaurants;
                    const gems = plan.discovery.hidden_gems;
                    const forecasts = plan.weather.daily_forecasts;

                    // Build day-by-day itinerary from best options
                    const days = Array.from({ length: numDays }, (_, i) => {
                      const dayDate = new Date(startDate);
                      dayDate.setDate(startDate.getDate() + i);
                      const dateStr = dayDate.toISOString().split("T")[0];
                      const dayNum = i + 1;
                      const isFirstDay = i === 0;
                      const isLastDay = i === numDays - 1;

                      // Match weather forecast
                      const weather = forecasts.find((f) => f.date === dateStr);

                      // Distribute attractions across days (2 per day: morning + afternoon)
                      const morningAtt = attractions[i * 2] || null;
                      const afternoonAtt = attractions[i * 2 + 1] || null;

                      // Assign restaurants (cycle through available)
                      const dayRestaurant = restaurants.length > 0 ? restaurants[i % restaurants.length] : null;

                      // Assign hidden gems (one every 2 days)
                      const dayGem = i % 2 === 1 && gems.length > 0 ? gems[Math.floor(i / 2) % gems.length] : null;

                      return { dayNum, dateStr, isFirstDay, isLastDay, weather, morningAtt, afternoonAtt, dayRestaurant, dayGem };
                    });

                    return (
                      <>
                        {/* Flight + Hotel summary banner */}
                        <div className="grid gap-4 sm:grid-cols-2">
                          {recFlight && recFlight.price_usd > 0 && (
                            <Card className="border-blue-200 bg-blue-50/50 dark:bg-blue-950/20">
                              <CardContent className="p-4">
                                <div className="flex items-center gap-2 mb-2">
                                  <Plane className="h-4 w-4 text-blue-600" />
                                  <span className="text-xs font-semibold uppercase tracking-wider text-blue-600">Your Flight</span>
                                </div>
                                <p className="font-semibold">{recFlight.airlines.join(", ")} — ${recFlight.price_usd}</p>
                                <p className="text-xs text-muted-foreground">
                                  {recFlight.stops === 0 ? "Direct" : `${recFlight.stops} stop(s)`} · {Math.floor(recFlight.total_duration_minutes / 60)}h {recFlight.total_duration_minutes % 60}m
                                </p>
                              </CardContent>
                            </Card>
                          )}
                          {recHotel && recHotel.total_rate_usd > 0 && (
                            <Card className="border-purple-200 bg-purple-50/50 dark:bg-purple-950/20">
                              <CardContent className="p-4">
                                <div className="flex items-center gap-2 mb-2">
                                  <Hotel className="h-4 w-4 text-purple-600" />
                                  <span className="text-xs font-semibold uppercase tracking-wider text-purple-600">Your Hotel</span>
                                </div>
                                <p className="font-semibold">{recHotel.name}</p>
                                <p className="text-xs text-muted-foreground">
                                  ${recHotel.rate_per_night_usd}/night · {recHotel.rating > 0 ? `★ ${recHotel.rating}` : ""} · Total: ${recHotel.total_rate_usd}
                                </p>
                              </CardContent>
                            </Card>
                          )}
                        </div>

                        {/* Day-by-day timeline */}
                        {days.map((day) => (
                          <Card key={day.dayNum} className="overflow-hidden">
                            <div className="flex items-center gap-3 border-b bg-muted/30 px-5 py-3">
                              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary font-bold text-white text-sm">
                                {day.dayNum}
                              </div>
                              <div className="flex-1 min-w-0">
                                <h3 className="font-serif text-lg font-semibold">
                                  Day {day.dayNum}{day.isFirstDay ? " — Arrival" : day.isLastDay ? " — Departure" : ""}
                                </h3>
                                <p className="text-xs text-muted-foreground">
                                  {new Date(day.dateStr + "T00:00:00").toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}
                                </p>
                              </div>
                              {day.weather && (
                                <div className="flex items-center gap-2 text-sm shrink-0">
                                  <Thermometer className="h-4 w-4 text-orange-500" />
                                  <span className="font-medium">{Math.round(day.weather.avg_temp_c)}°C</span>
                                  <Badge variant="outline" className="text-[10px] capitalize">{day.weather.dominant_condition}</Badge>
                                </div>
                              )}
                            </div>
                            <CardContent className="p-5 space-y-4">
                              {/* Arrival info on first day */}
                              {day.isFirstDay && recFlight && recFlight.price_usd > 0 && (
                                <div className="flex items-start gap-3">
                                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/30">
                                    <Plane className="h-4 w-4 text-blue-600" />
                                  </div>
                                  <div>
                                    <p className="text-sm font-semibold">Arrive via {recFlight.airlines.join(", ")}</p>
                                    <p className="text-xs text-muted-foreground">Check in to {recHotel?.name || "your hotel"}</p>
                                  </div>
                                </div>
                              )}

                              {/* Morning activity */}
                              {day.morningAtt && (
                                <div className="flex items-start gap-3 cursor-pointer group" onClick={() => setSelectedAttraction(day.morningAtt)}>
                                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-amber-100 dark:bg-amber-900/30">
                                    <Sun className="h-4 w-4 text-amber-600" />
                                  </div>
                                  <div className="min-w-0">
                                    <p className="text-xs font-semibold uppercase tracking-wider text-amber-600 mb-0.5">Morning</p>
                                    <p className="text-sm font-semibold group-hover:text-primary transition-colors">{day.morningAtt.name}</p>
                                    {day.morningAtt.description && <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5">{day.morningAtt.description}</p>}
                                    <div className="flex items-center gap-2 mt-1">
                                      {day.morningAtt.rating > 0 && <span className="flex items-center gap-0.5 text-xs"><Star className="h-3 w-3 fill-amber-400 text-amber-400" />{day.morningAtt.rating}</span>}
                                      {day.morningAtt.type && <Badge variant="secondary" className="text-[10px] capitalize">{day.morningAtt.type}</Badge>}
                                    </div>
                                  </div>
                                </div>
                              )}

                              {/* Lunch */}
                              {day.dayRestaurant && (
                                <div className="flex items-start gap-3">
                                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-orange-100 dark:bg-orange-900/30">
                                    <Utensils className="h-4 w-4 text-orange-600" />
                                  </div>
                                  <div>
                                    <p className="text-xs font-semibold uppercase tracking-wider text-orange-600 mb-0.5">Lunch</p>
                                    <p className="text-sm font-semibold">{day.dayRestaurant.name}</p>
                                    <div className="flex items-center gap-2 mt-1">
                                      {day.dayRestaurant.rating > 0 && <span className="flex items-center gap-0.5 text-xs"><Star className="h-3 w-3 fill-amber-400 text-amber-400" />{day.dayRestaurant.rating}</span>}
                                      {day.dayRestaurant.type && <Badge variant="secondary" className="text-[10px] capitalize">{day.dayRestaurant.type}</Badge>}
                                      {day.dayRestaurant.price_level && <Badge variant="outline" className="text-[10px]">{day.dayRestaurant.price_level}</Badge>}
                                    </div>
                                  </div>
                                </div>
                              )}

                              {/* Afternoon activity */}
                              {day.afternoonAtt && (
                                <div className="flex items-start gap-3 cursor-pointer group" onClick={() => setSelectedAttraction(day.afternoonAtt)}>
                                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-sky-100 dark:bg-sky-900/30">
                                    <Moon className="h-4 w-4 text-sky-600" />
                                  </div>
                                  <div className="min-w-0">
                                    <p className="text-xs font-semibold uppercase tracking-wider text-sky-600 mb-0.5">Afternoon</p>
                                    <p className="text-sm font-semibold group-hover:text-primary transition-colors">{day.afternoonAtt.name}</p>
                                    {day.afternoonAtt.description && <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5">{day.afternoonAtt.description}</p>}
                                    <div className="flex items-center gap-2 mt-1">
                                      {day.afternoonAtt.rating > 0 && <span className="flex items-center gap-0.5 text-xs"><Star className="h-3 w-3 fill-amber-400 text-amber-400" />{day.afternoonAtt.rating}</span>}
                                      {day.afternoonAtt.type && <Badge variant="secondary" className="text-[10px] capitalize">{day.afternoonAtt.type}</Badge>}
                                    </div>
                                  </div>
                                </div>
                              )}

                              {/* Hidden gem */}
                              {day.dayGem && (
                                <div className="flex items-start gap-3 cursor-pointer group" onClick={() => setSelectedGem(day.dayGem)}>
                                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                                    <Gem className="h-4 w-4 text-primary" />
                                  </div>
                                  <div className="min-w-0">
                                    <p className="text-xs font-semibold uppercase tracking-wider text-primary mb-0.5">Hidden Gem</p>
                                    <p className="text-sm font-semibold group-hover:text-primary transition-colors">{day.dayGem.name}</p>
                                    <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5">{day.dayGem.snippet}</p>
                                  </div>
                                </div>
                              )}

                              {/* Evening on non-first/last day or if no activities */}
                              {!day.isFirstDay && !day.isLastDay && !day.morningAtt && !day.afternoonAtt && (
                                <div className="flex items-start gap-3">
                                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-muted">
                                    <Coffee className="h-4 w-4 text-muted-foreground" />
                                  </div>
                                  <div>
                                    <p className="text-sm font-semibold">Free day — explore at your own pace</p>
                                    <p className="text-xs text-muted-foreground">Wander the streets, visit local markets, or relax at the hotel.</p>
                                  </div>
                                </div>
                              )}

                              {/* Departure on last day */}
                              {day.isLastDay && (
                                <div className="flex items-start gap-3">
                                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/30">
                                    <Plane className="h-4 w-4 text-blue-600" />
                                  </div>
                                  <div>
                                    <p className="text-sm font-semibold">Check out & depart</p>
                                    <p className="text-xs text-muted-foreground">Head to the airport for your return flight.</p>
                                  </div>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        ))}
                      </>
                    );
                  })()}
                </TabsContent>

                {/* Weather */}
                <TabsContent value="weather" className="space-y-4">
                  <Card className="border-none bg-sky-50/50 dark:bg-sky-950/20">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <CloudSun className="h-5 w-5 text-sky-600" />
                        <h3 className="font-semibold">Forecast Summary</h3>
                      </div>
                      <p className="text-sm text-muted-foreground">{plan.weather.summary}</p>
                      <Badge variant={plan.weather.outdoor_viable ? "default" : "secondary"} className="mt-2">
                        {plan.weather.outdoor_viable ? "✅ Good for outdoor activities" : "⚠️ Limited outdoor viability"}
                      </Badge>
                    </CardContent>
                  </Card>
                  {plan.weather.daily_forecasts.length > 0 ? (
                    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                      {plan.weather.daily_forecasts.map((day, i) => (
                        <Card key={i}>
                          <CardContent className="p-4">
                            <p className="text-sm font-medium text-muted-foreground">{day.date}</p>
                            <div className="mt-2 flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <Thermometer className="h-4 w-4 text-orange-500" />
                                <span className="text-lg font-bold">{Math.round(day.avg_temp_c)}°C</span>
                              </div>
                              <Badge variant="outline" className="capitalize">{day.dominant_condition}</Badge>
                            </div>
                            <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
                              <Droplets className="h-3 w-3" />
                              Rain: {Math.round(day.max_rain_probability * 100)}%
                            </div>
                            <p className="mt-2 text-xs text-muted-foreground">{day.summary}</p>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground italic">No daily forecast data — dates may be too far in the future.</p>
                  )}
                </TabsContent>

                {/* Transport */}
                <TabsContent value="transport" className="space-y-4">
                  {plan.transport.options.length > 0 ? (
                    <div className="grid gap-4 sm:grid-cols-2">
                      {plan.transport.options.map((opt, i) => (
                        <Card key={i} className={cn("overflow-hidden transition-all hover:shadow-md", opt.tag === "best_value" && "border-primary")}>
                          <CardContent className="p-0">
                            <div className="flex items-center justify-between bg-muted/30 p-4">
                              <div className="flex items-center gap-3">
                                <div className="rounded-lg bg-background p-2 shadow-sm"><Plane className="h-5 w-5 text-primary" /></div>
                                <div>
                                  <h3 className="font-semibold">{opt.airlines.join(", ")}</h3>
                                  <p className="text-xs text-muted-foreground">{opt.stops === 0 ? "Direct" : `${opt.stops} stop${opt.stops > 1 ? "s" : ""}`}</p>
                                </div>
                              </div>
                              <div className="text-right">
                                <span className="block text-lg font-bold">${opt.price_usd}</span>
                                {opt.tag && <Badge variant={opt.tag === "best_value" ? "default" : "secondary"} className="text-[10px] capitalize">{opt.tag.replace("_", " ")}</Badge>}
                              </div>
                            </div>
                            <div className="grid grid-cols-3 gap-4 p-4 text-center">
                              <div>
                                <span className="block text-lg font-medium">{opt.legs[0]?.departure_time?.split(" ")[1] || "—"}</span>
                                <span className="text-xs text-muted-foreground">{opt.legs[0]?.departure_airport || ""}</span>
                              </div>
                              <div className="flex flex-col items-center justify-center">
                                <span className="text-xs text-muted-foreground mb-1">{Math.floor(opt.total_duration_minutes / 60)}h {opt.total_duration_minutes % 60}m</span>
                                <div className="h-[2px] w-full bg-border relative">
                                  <div className="absolute left-0 -top-1 h-2 w-2 rounded-full bg-primary" />
                                  <div className="absolute right-0 -top-1 h-2 w-2 rounded-full bg-border" />
                                </div>
                              </div>
                              <div>
                                <span className="block text-lg font-medium">{opt.legs[opt.legs.length - 1]?.arrival_time?.split(" ")[1] || "—"}</span>
                                <span className="text-xs text-muted-foreground">{opt.legs[opt.legs.length - 1]?.arrival_airport || ""}</span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground italic">No flight options found.</p>
                  )}
                  {plan.transport.recommended && plan.transport.recommended.price_usd > 0 && (
                    <Card className="border-primary/20 bg-primary/5">
                      <CardContent className="p-4 flex items-center gap-3">
                        <Sparkles className="h-5 w-5 text-primary shrink-0" />
                        <div>
                          <p className="text-sm font-semibold">Recommended: {plan.transport.recommended.airlines.join(", ")} — ${plan.transport.recommended.price_usd}</p>
                          <p className="text-xs text-muted-foreground">
                            {plan.transport.recommended.stops === 0 ? "Direct" : `${plan.transport.recommended.stops} stop(s)`} · {Math.floor(plan.transport.recommended.total_duration_minutes / 60)}h {plan.transport.recommended.total_duration_minutes % 60}m · Est. round-trip: ${plan.transport.estimated_cost_usd}
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </TabsContent>

                {/* Hotels */}
                <TabsContent value="hotels">
                  {plan.hotel.options.length > 0 ? (
                    <div className="grid gap-6 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                      {plan.hotel.options.map((hotel, i) => {
                        const isRec = hotel.name === plan.hotel.recommended?.name;
                        return (
                          <Card key={i} className={cn("group overflow-hidden", isRec && "border-primary")}>
                            <CardContent className="p-4">
                              <div className="flex items-start justify-between">
                                <div className="flex-1 min-w-0">
                                  <h3 className="font-serif text-lg font-semibold truncate">{hotel.name}</h3>
                                  {hotel.location && <p className="text-xs text-muted-foreground mt-0.5 truncate">{hotel.location}</p>}
                                </div>
                                <div className="flex items-center gap-1 text-sm font-medium ml-2 shrink-0">
                                  <Star className="h-3 w-3 fill-amber-400 text-amber-400" />{hotel.rating}
                                </div>
                              </div>
                              <div className="mt-3 flex items-center justify-between">
                                <span className="text-lg font-bold text-primary">${hotel.rate_per_night_usd}/night</span>
                                <span className="text-sm text-muted-foreground">Total: ${hotel.total_rate_usd}</span>
                              </div>
                              {hotel.reviews > 0 && <p className="text-xs text-muted-foreground mt-1">{hotel.reviews.toLocaleString()} reviews</p>}
                              {hotel.amenities.length > 0 && (
                                <div className="mt-3 flex flex-wrap gap-1.5">
                                  {hotel.amenities.slice(0, 4).map((a) => (
                                    <Badge key={a} variant="outline" className="bg-muted/50 font-normal text-[10px]">{a}</Badge>
                                  ))}
                                  {hotel.amenities.length > 4 && <Badge variant="outline" className="bg-muted/50 font-normal text-[10px]">+{hotel.amenities.length - 4} more</Badge>}
                                </div>
                              )}
                              {isRec && <Badge className="mt-3 bg-primary/10 text-primary">✅ Recommended</Badge>}
                              {hotel.link && (
                                <Button className="mt-4 w-full" variant="outline" asChild>
                                  <a href={hotel.link} target="_blank" rel="noopener noreferrer">View Details</a>
                                </Button>
                              )}
                            </CardContent>
                          </Card>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground italic">No hotel options found.</p>
                  )}
                </TabsContent>

                {/* Discoveries */}
                <TabsContent value="discoveries" className="space-y-8">
                  {plan.discovery.attractions.length > 0 && (
                    <div>
                      <h3 className="text-lg font-serif font-semibold mb-4">🏛️ Top Attractions</h3>
                      <div className="grid gap-4 sm:grid-cols-2">
                        {plan.discovery.attractions.map((att, i) => (
                          <Card key={i} className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setSelectedAttraction(att)}>
                            <CardContent className="p-4">
                              <div className="flex items-start justify-between">
                                <h4 className="font-semibold">{att.name}</h4>
                                {att.rating > 0 && <span className="flex items-center gap-1 text-sm shrink-0 ml-2"><Star className="h-3 w-3 fill-amber-400 text-amber-400" />{att.rating}</span>}
                              </div>
                              {att.description && <p className="mt-1 text-sm text-muted-foreground line-clamp-2">{att.description}</p>}
                              <div className="mt-2 flex gap-2">
                                {att.type && <Badge variant="secondary" className="capitalize">{att.type}</Badge>}
                                {att.is_outdoor && <Badge variant="outline">Outdoor</Badge>}
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </div>
                  )}
                  {plan.discovery.hidden_gems.length > 0 && (
                    <div>
                      <h3 className="text-lg font-serif font-semibold mb-4">💎 Hidden Gems</h3>
                      <div className="grid gap-4 sm:grid-cols-2">
                        {plan.discovery.hidden_gems.map((gem, i) => (
                          <Card key={i} className="border-primary/20 bg-primary/5 cursor-pointer hover:shadow-md transition-shadow" onClick={() => setSelectedGem(gem)}>
                            <CardContent className="p-4">
                              <div className="flex items-center gap-2">
                                <Gem className="h-4 w-4 text-primary shrink-0" />
                                <h4 className="font-semibold">{gem.name}</h4>
                              </div>
                              <p className="mt-1 text-sm text-muted-foreground line-clamp-2">{gem.snippet}</p>
                              <span className="mt-2 block text-xs text-muted-foreground">Source: {gem.source} · {gem.mentions} mentions</span>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </div>
                  )}
                  {plan.discovery.restaurants.length > 0 && (
                    <div>
                      <h3 className="text-lg font-serif font-semibold mb-4">🍽️ Restaurants</h3>
                      <div className="grid gap-4 sm:grid-cols-2">
                        {plan.discovery.restaurants.map((rest, i) => (
                          <Card key={i}>
                            <CardContent className="p-4">
                              <div className="flex items-start justify-between">
                                <h4 className="font-semibold">{rest.name}</h4>
                                {rest.rating > 0 && <span className="flex items-center gap-1 text-sm shrink-0 ml-2"><Star className="h-3 w-3 fill-amber-400 text-amber-400" />{rest.rating}</span>}
                              </div>
                              <div className="mt-2 flex gap-2">
                                {rest.type && <Badge variant="secondary" className="capitalize">{rest.type}</Badge>}
                                {rest.price_level && <Badge variant="outline">{rest.price_level}</Badge>}
                              </div>
                              {rest.address && <p className="mt-2 text-xs text-muted-foreground">📍 {rest.address}</p>}
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </div>
                  )}
                  {plan.discovery.attractions.length === 0 && plan.discovery.hidden_gems.length === 0 && plan.discovery.restaurants.length === 0 && (
                    <p className="text-sm text-muted-foreground italic">No discovery data found.</p>
                  )}
                </TabsContent>
              </div>
            </Tabs>
          </div>
        </div>

        {/* Chat Sidebar */}
        <div className={cn(
          "fixed inset-y-0 right-0 z-50 w-80 transform border-l bg-background shadow-2xl transition-transform duration-300 ease-in-out md:relative md:translate-x-0 md:shadow-none",
          chatOpen ? "translate-x-0" : "translate-x-full md:hidden"
        )}>
          <div className="flex h-full flex-col">
            <div className="flex items-center justify-between border-b p-4">
              <div className="flex items-center gap-2">
                <div className="rounded-full bg-primary/10 p-1.5"><MessageSquare className="h-4 w-4 text-primary" /></div>
                <h3 className="font-semibold">Trip Assistant</h3>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setChatOpen(false)} className="md:hidden">
                <span className="sr-only">Close</span>
                <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg" className="h-4 w-4"><path d="M11.7816 4.03157C12.0062 3.80702 12.0062 3.44295 11.7816 3.2184C11.5571 2.99385 11.193 2.99385 10.9685 3.2184L7.50005 6.68682L4.03164 3.2184C3.80708 2.99385 3.44301 2.99385 3.21846 3.2184C2.99391 3.44295 2.99391 3.80702 3.21846 4.03157L6.68688 7.49999L3.21846 10.9684C2.99391 11.193 2.99391 11.557 3.21846 11.7816C3.44301 12.0061 3.80708 12.0061 4.03164 11.7816L7.50005 8.31316L10.9685 11.7816C11.193 12.0061 11.5571 12.0061 11.7816 11.7816C12.0062 11.557 12.0062 11.193 11.7816 10.9684L8.31322 7.49999L11.7816 4.03157Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path></svg>
              </Button>
            </div>
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4">
                {messages.map((msg, i) => (
                  <div key={i} className={cn("flex gap-3", msg.role === "user" && "flex-row-reverse")}>
                    <div className={cn("h-8 w-8 shrink-0 rounded-full flex items-center justify-center text-xs font-bold", msg.role === "assistant" ? "bg-primary/10 text-primary" : "bg-primary text-white")}>
                      {msg.role === "assistant" ? "AI" : "Me"}
                    </div>
                    <div className={cn("rounded-2xl px-4 py-3 text-sm max-w-[220px]", msg.role === "assistant" ? "rounded-tl-none bg-muted" : "rounded-tr-none bg-primary text-white shadow-sm whitespace-pre-wrap")}>
                      {msg.role === "assistant" ? (
                        <div className="prose prose-sm dark:prose-invert max-w-none [&_p]:my-1 [&_ul]:my-1 [&_li]:my-0">
                          <Markdown>{msg.content}</Markdown>
                        </div>
                      ) : msg.content}
                    </div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="flex gap-3">
                    <div className="h-8 w-8 shrink-0 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary">AI</div>
                    <div className="rounded-2xl rounded-tl-none bg-muted px-4 py-3 text-sm">
                      <span className="inline-flex gap-1">
                        <span className="animate-bounce">●</span>
                        <span className="animate-bounce" style={{ animationDelay: "0.1s" }}>●</span>
                        <span className="animate-bounce" style={{ animationDelay: "0.2s" }}>●</span>
                      </span>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>
            </ScrollArea>
            <div className="border-t p-4">
              <form onSubmit={(e) => { e.preventDefault(); handleSendChat(); }} className="relative">
                <input type="text" placeholder="Ask for changes..." value={chatInput} onChange={(e) => setChatInput(e.target.value)} disabled={chatLoading}
                  className="w-full rounded-full border bg-background pl-4 pr-10 py-3 text-sm shadow-sm outline-none focus:ring-1 focus:ring-primary disabled:opacity-50" />
                <Button type="submit" size="icon" disabled={chatLoading || !chatInput.trim()} className="absolute right-1 top-1 h-8 w-8 rounded-full">
                  <Send className="h-4 w-4" />
                </Button>
              </form>
            </div>
          </div>
        </div>

        {!chatOpen && (
          <Button className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-xl z-50" onClick={() => setChatOpen(true)}>
            <MessageSquare className="h-6 w-6" />
          </Button>
        )}

        {/* Attraction Dialog */}
        <Dialog open={!!selectedAttraction} onOpenChange={(open) => !open && setSelectedAttraction(null)}>
          <DialogContent className="sm:max-w-[500px]">
            {selectedAttraction && (
              <div className="space-y-4">
                <DialogHeader>
                  <DialogTitle className="font-serif text-2xl">{selectedAttraction.name}</DialogTitle>
                  {selectedAttraction.rating > 0 && (
                    <div className="flex items-center gap-2 mt-1 text-sm font-medium">
                      <Star className="h-4 w-4 fill-amber-400 text-amber-400" />{selectedAttraction.rating}
                      {selectedAttraction.reviews > 0 && <span className="text-muted-foreground">({selectedAttraction.reviews} reviews)</span>}
                    </div>
                  )}
                </DialogHeader>
                {selectedAttraction.description && <p className="text-foreground leading-relaxed">{selectedAttraction.description}</p>}
                <div className="flex flex-wrap gap-2">
                  {selectedAttraction.type && <Badge variant="secondary" className="capitalize">{selectedAttraction.type}</Badge>}
                  {selectedAttraction.is_outdoor && <Badge variant="outline">Outdoor</Badge>}
                </div>
                {selectedAttraction.address && <p className="text-sm text-muted-foreground">📍 {selectedAttraction.address}</p>}
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* Hidden Gem Dialog */}
        <Dialog open={!!selectedGem} onOpenChange={(open) => !open && setSelectedGem(null)}>
          <DialogContent className="sm:max-w-[500px]">
            {selectedGem && (
              <div className="space-y-4">
                <DialogHeader>
                  <DialogTitle className="font-serif text-2xl flex items-center gap-2">
                    <Gem className="h-6 w-6 text-primary" />
                    {selectedGem.name}
                  </DialogTitle>
                </DialogHeader>
                <div className="rounded-lg border border-primary/20 bg-primary/5 p-4">
                  <p className="text-foreground leading-relaxed">{selectedGem.snippet}</p>
                </div>
                <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                  {selectedGem.source && (
                    <div className="flex items-center gap-1.5">
                      <Badge variant="secondary" className="capitalize">{selectedGem.source}</Badge>
                    </div>
                  )}
                  {selectedGem.mentions > 0 && (
                    <span>{selectedGem.mentions} mention{selectedGem.mentions !== 1 ? "s" : ""} online</span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground italic">
                  This is a local favorite discovered through community recommendations — not a typical tourist attraction.
                </p>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
      <Toaster />
    </Layout>
  );
}
