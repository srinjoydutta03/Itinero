
export interface TripDetails {
  destination: string;
  dates: { from: Date | undefined; to: Date | undefined };
  travelers: number;
  budget: number;
}

export interface Activity {
  id: string;
  name: string;
  type: "outdoor" | "culture" | "food" | "relax";
  time: string;
  cost: number;
  description: string;
  image: string;
  rating: number;
}

export interface DayPlan {
  day: number;
  date: string;
  weather: { temp: number; condition: "sunny" | "cloudy" | "rainy" };
  activities: Activity[];
}

export interface Hotel {
  id: string;
  name: string;
  stars: number;
  pricePerNight: number;
  totalPrice: number;
  image: string;
  rating: number;
  amenities: string[];
}

export interface TransportOption {
  type: "flight" | "train" | "bus";
  provider: string;
  duration: string;
  pricePerPerson: number;
  totalPrice: number;
  departure: string;
  arrival: string;
}

export interface Itinerary {
  id: string;
  destination: string;
  totalCost: number;
  remainingBudget: number;
  weatherSummary: string;
  transport: TransportOption[];
  hotels: Hotel[];
  days: DayPlan[];
  restaurants: Activity[]; 
}

export const generateMockItinerary = (details: TripDetails): Itinerary => {
  const { destination, travelers, budget } = details;
  
  // Scale costs based on travelers
  const transportCost = 350 * travelers;
  const hotelCost = 200 * 5; // 5 nights approx
  const foodCost = 50 * travelers * 5;
  const activityCost = 100 * travelers;
  
  const totalCost = transportCost + hotelCost + foodCost + activityCost;
  const remaining = budget - totalCost;

  return {
    id: "trip-123",
    destination: destination || "Paris, France",
    totalCost,
    remainingBudget: remaining,
    weatherSummary: "Mostly sunny with a chance of light rain on Day 3. Pack light layers.",
    transport: [
      {
        type: "flight",
        provider: "AirFrance",
        duration: "7h 20m",
        pricePerPerson: 350,
        totalPrice: 350 * travelers,
        departure: "10:00 AM",
        arrival: "5:20 PM"
      },
      {
        type: "train",
        provider: "Eurostar",
        duration: "2h 15m",
        pricePerPerson: 120,
        totalPrice: 120 * travelers,
        departure: "08:00 AM",
        arrival: "10:15 AM"
      }
    ],
    hotels: [
      {
        id: "h1",
        name: "Grand Hôtel du Palais",
        stars: 5,
        pricePerNight: 450,
        totalPrice: 450 * 5,
        image: "/src/assets/hotel-1.jpg",
        rating: 4.8,
        amenities: ["Spa", "Pool", "City View"]
      },
      {
        id: "h2",
        name: "Le Charme Boutique",
        stars: 4,
        pricePerNight: 220,
        totalPrice: 220 * 5,
        image: "/src/assets/hotel-2.jpg",
        rating: 4.5,
        amenities: ["Breakfast", "Central", "Cozy"]
      },
       {
        id: "h3",
        name: "Modern Loft Stay",
        stars: 4,
        pricePerNight: 180,
        totalPrice: 180 * 5,
        image: "/src/assets/hotel-3.jpg",
        rating: 4.2,
        amenities: ["Kitchen", "WiFi", "Worksafe"]
      }
    ],
    restaurants: [
      {
        id: "r1",
        name: "Le Petit Bistro",
        type: "food",
        time: "7:00 PM",
        cost: 45 * travelers,
        description: "Classic French bistro with amazing onion soup.",
        image: "/src/assets/food-1.jpg",
        rating: 4.7
      },
      {
        id: "r2",
        name: "L'Orangerie",
        type: "food",
        time: "8:00 PM",
        cost: 120 * travelers,
        description: "Fine dining experience in a glass conservatory.",
        image: "/src/assets/food-2.jpg",
        rating: 4.9
      }
    ],
    days: [
      {
        day: 1,
        date: "Mon, Oct 12",
        weather: { temp: 18, condition: "sunny" },
        activities: [
          {
            id: "a1",
            name: "Arrival & Check-in",
            type: "relax",
            time: "2:00 PM",
            cost: 0,
            description: "Settle into your hotel and freshen up.",
            image: "/src/assets/hotel-1.jpg",
            rating: 0
          },
          {
            id: "a2",
            name: "Sunset Seine Cruise",
            type: "relax",
            time: "6:00 PM",
            cost: 25 * travelers,
            description: "Watch the city lights come alive from the river.",
            image: "/src/assets/activity-1.jpg",
            rating: 4.5
          }
        ]
      },
      {
        day: 2,
        date: "Tue, Oct 13",
        weather: { temp: 19, condition: "cloudy" },
        activities: [
          {
            id: "a3",
            name: "Louvre Museum Tour",
            type: "culture",
            time: "10:00 AM",
            cost: 20 * travelers,
            description: "Skip-the-line guided tour of the masterpieces.",
            image: "/src/assets/activity-2.jpg",
            rating: 4.8
          },
           {
            id: "a4",
            name: "Montmartre Food Walk",
            type: "food",
            time: "1:00 PM",
            cost: 60 * travelers,
            description: "Taste the best cheese and wine in the artist district.",
            image: "/src/assets/food-1.jpg",
            rating: 4.9
          }
        ]
      },
      {
        day: 3,
        date: "Wed, Oct 14",
        weather: { temp: 16, condition: "rainy" },
        activities: [
           {
            id: "a5",
            name: "Indoor Market Exploration",
            type: "food",
            time: "11:00 AM",
            cost: 0,
            description: "Visit the covered passages and antique shops.",
            image: "/src/assets/activity-2.jpg",
            rating: 4.3
          }
        ]
      }
    ]
  };
};
