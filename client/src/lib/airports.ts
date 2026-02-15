export interface Airport {
  city: string;
  name: string;
  iata: string;
  country: string;
}

/**
 * Comprehensive list of major world airports for autocomplete.
 * Sorted alphabetically by city name.
 */
export const AIRPORTS: Airport[] = [
  // A
  { city: "Abu Dhabi", name: "Zayed International Airport", iata: "AUH", country: "UAE" },
  { city: "Accra", name: "Kotoka International Airport", iata: "ACC", country: "Ghana" },
  { city: "Addis Ababa", name: "Bole International Airport", iata: "ADD", country: "Ethiopia" },
  { city: "Adelaide", name: "Adelaide Airport", iata: "ADL", country: "Australia" },
  { city: "Ahmedabad", name: "Sardar Vallabhbhai Patel International Airport", iata: "AMD", country: "India" },
  { city: "Amman", name: "Queen Alia International Airport", iata: "AMM", country: "Jordan" },
  { city: "Amsterdam", name: "Schiphol Airport", iata: "AMS", country: "Netherlands" },
  { city: "Anchorage", name: "Ted Stevens Anchorage International Airport", iata: "ANC", country: "USA" },
  { city: "Ankara", name: "Esenboğa International Airport", iata: "ESB", country: "Turkey" },
  { city: "Athens", name: "Eleftherios Venizelos International Airport", iata: "ATH", country: "Greece" },
  { city: "Atlanta", name: "Hartsfield-Jackson Atlanta International Airport", iata: "ATL", country: "USA" },
  { city: "Auckland", name: "Auckland Airport", iata: "AKL", country: "New Zealand" },
  { city: "Austin", name: "Austin-Bergstrom International Airport", iata: "AUS", country: "USA" },

  // B
  { city: "Baku", name: "Heydar Aliyev International Airport", iata: "GYD", country: "Azerbaijan" },
  { city: "Bali", name: "Ngurah Rai International Airport", iata: "DPS", country: "Indonesia" },
  { city: "Baltimore", name: "Baltimore/Washington International Airport", iata: "BWI", country: "USA" },
  { city: "Bangkok", name: "Suvarnabhumi Airport", iata: "BKK", country: "Thailand" },
  { city: "Barcelona", name: "Josep Tarradellas Barcelona–El Prat Airport", iata: "BCN", country: "Spain" },
  { city: "Beijing", name: "Capital International Airport", iata: "PEK", country: "China" },
  { city: "Beijing", name: "Daxing International Airport", iata: "PKX", country: "China" },
  { city: "Beirut", name: "Rafic Hariri International Airport", iata: "BEY", country: "Lebanon" },
  { city: "Belgrade", name: "Nikola Tesla Airport", iata: "BEG", country: "Serbia" },
  { city: "Bengaluru", name: "Kempegowda International Airport", iata: "BLR", country: "India" },
  { city: "Bergen", name: "Bergen Airport, Flesland", iata: "BGO", country: "Norway" },
  { city: "Berlin", name: "Berlin Brandenburg Airport", iata: "BER", country: "Germany" },
  { city: "Bogotá", name: "El Dorado International Airport", iata: "BOG", country: "Colombia" },
  { city: "Bologna", name: "Guglielmo Marconi Airport", iata: "BLQ", country: "Italy" },
  { city: "Boston", name: "Logan International Airport", iata: "BOS", country: "USA" },
  { city: "Brisbane", name: "Brisbane Airport", iata: "BNE", country: "Australia" },
  { city: "Brussels", name: "Brussels Airport", iata: "BRU", country: "Belgium" },
  { city: "Bucharest", name: "Henri Coandă International Airport", iata: "OTP", country: "Romania" },
  { city: "Budapest", name: "Budapest Ferenc Liszt International Airport", iata: "BUD", country: "Hungary" },
  { city: "Buenos Aires", name: "Ministro Pistarini International Airport", iata: "EZE", country: "Argentina" },
  { city: "Buffalo", name: "Buffalo Niagara International Airport", iata: "BUF", country: "USA" },

  // C
  { city: "Cairo", name: "Cairo International Airport", iata: "CAI", country: "Egypt" },
  { city: "Calgary", name: "Calgary International Airport", iata: "YYC", country: "Canada" },
  { city: "Cancún", name: "Cancún International Airport", iata: "CUN", country: "Mexico" },
  { city: "Cape Town", name: "Cape Town International Airport", iata: "CPT", country: "South Africa" },
  { city: "Casablanca", name: "Mohammed V International Airport", iata: "CMN", country: "Morocco" },
  { city: "Charlotte", name: "Charlotte Douglas International Airport", iata: "CLT", country: "USA" },
  { city: "Chennai", name: "Chennai International Airport", iata: "MAA", country: "India" },
  { city: "Chicago", name: "O'Hare International Airport", iata: "ORD", country: "USA" },
  { city: "Chicago", name: "Midway International Airport", iata: "MDW", country: "USA" },
  { city: "Christchurch", name: "Christchurch Airport", iata: "CHC", country: "New Zealand" },
  { city: "Cincinnati", name: "Cincinnati/Northern Kentucky International Airport", iata: "CVG", country: "USA" },
  { city: "Cleveland", name: "Cleveland Hopkins International Airport", iata: "CLE", country: "USA" },
  { city: "Colombo", name: "Bandaranaike International Airport", iata: "CMB", country: "Sri Lanka" },
  { city: "Columbus", name: "John Glenn Columbus International Airport", iata: "CMH", country: "USA" },
  { city: "Copenhagen", name: "Copenhagen Airport", iata: "CPH", country: "Denmark" },

  // D
  { city: "Dallas", name: "Dallas/Fort Worth International Airport", iata: "DFW", country: "USA" },
  { city: "Dallas", name: "Dallas Love Field", iata: "DAL", country: "USA" },
  { city: "Dar es Salaam", name: "Julius Nyerere International Airport", iata: "DAR", country: "Tanzania" },
  { city: "Delhi", name: "Indira Gandhi International Airport", iata: "DEL", country: "India" },
  { city: "Denver", name: "Denver International Airport", iata: "DEN", country: "USA" },
  { city: "Detroit", name: "Detroit Metropolitan Wayne County Airport", iata: "DTW", country: "USA" },
  { city: "Dhaka", name: "Hazrat Shahjalal International Airport", iata: "DAC", country: "Bangladesh" },
  { city: "Doha", name: "Hamad International Airport", iata: "DOH", country: "Qatar" },
  { city: "Dubai", name: "Dubai International Airport", iata: "DXB", country: "UAE" },
  { city: "Dubai", name: "Al Maktoum International Airport", iata: "DWC", country: "UAE" },
  { city: "Dublin", name: "Dublin Airport", iata: "DUB", country: "Ireland" },
  { city: "Düsseldorf", name: "Düsseldorf Airport", iata: "DUS", country: "Germany" },

  // E
  { city: "Edinburgh", name: "Edinburgh Airport", iata: "EDI", country: "UK" },
  { city: "Edmonton", name: "Edmonton International Airport", iata: "YEG", country: "Canada" },

  // F
  { city: "Florence", name: "Florence Airport", iata: "FLR", country: "Italy" },
  { city: "Fort Lauderdale", name: "Fort Lauderdale-Hollywood International Airport", iata: "FLL", country: "USA" },
  { city: "Frankfurt", name: "Frankfurt Airport", iata: "FRA", country: "Germany" },
  { city: "Fukuoka", name: "Fukuoka Airport", iata: "FUK", country: "Japan" },

  // G
  { city: "Geneva", name: "Geneva Airport", iata: "GVA", country: "Switzerland" },
  { city: "Goa", name: "Manohar International Airport", iata: "GOX", country: "India" },
  { city: "Gothenburg", name: "Göteborg Landvetter Airport", iata: "GOT", country: "Sweden" },
  { city: "Guangzhou", name: "Baiyun International Airport", iata: "CAN", country: "China" },

  // H
  { city: "Hamburg", name: "Hamburg Airport", iata: "HAM", country: "Germany" },
  { city: "Hanoi", name: "Noi Bai International Airport", iata: "HAN", country: "Vietnam" },
  { city: "Havana", name: "José Martí International Airport", iata: "HAV", country: "Cuba" },
  { city: "Helsinki", name: "Helsinki-Vantaa Airport", iata: "HEL", country: "Finland" },
  { city: "Ho Chi Minh City", name: "Tan Son Nhat International Airport", iata: "SGN", country: "Vietnam" },
  { city: "Hong Kong", name: "Hong Kong International Airport", iata: "HKG", country: "China" },
  { city: "Honolulu", name: "Daniel K. Inouye International Airport", iata: "HNL", country: "USA" },
  { city: "Houston", name: "George Bush Intercontinental Airport", iata: "IAH", country: "USA" },
  { city: "Houston", name: "William P. Hobby Airport", iata: "HOU", country: "USA" },
  { city: "Hyderabad", name: "Rajiv Gandhi International Airport", iata: "HYD", country: "India" },

  // I
  { city: "Indianapolis", name: "Indianapolis International Airport", iata: "IND", country: "USA" },
  { city: "Islamabad", name: "Islamabad International Airport", iata: "ISB", country: "Pakistan" },
  { city: "Istanbul", name: "Istanbul Airport", iata: "IST", country: "Turkey" },
  { city: "Istanbul", name: "Sabiha Gökçen International Airport", iata: "SAW", country: "Turkey" },

  // J
  { city: "Jaipur", name: "Jaipur International Airport", iata: "JAI", country: "India" },
  { city: "Jakarta", name: "Soekarno-Hatta International Airport", iata: "CGK", country: "Indonesia" },
  { city: "Jeddah", name: "King Abdulaziz International Airport", iata: "JED", country: "Saudi Arabia" },
  { city: "Johannesburg", name: "O.R. Tambo International Airport", iata: "JNB", country: "South Africa" },

  // K
  { city: "Kansas City", name: "Kansas City International Airport", iata: "MCI", country: "USA" },
  { city: "Karachi", name: "Jinnah International Airport", iata: "KHI", country: "Pakistan" },
  { city: "Kathmandu", name: "Tribhuvan International Airport", iata: "KTM", country: "Nepal" },
  { city: "Kochi", name: "Cochin International Airport", iata: "COK", country: "India" },
  { city: "Kolkata", name: "Netaji Subhas Chandra Bose International Airport", iata: "CCU", country: "India" },
  { city: "Kuala Lumpur", name: "Kuala Lumpur International Airport", iata: "KUL", country: "Malaysia" },
  { city: "Kuwait City", name: "Kuwait International Airport", iata: "KWI", country: "Kuwait" },
  { city: "Kyoto", name: "Kansai International Airport", iata: "KIX", country: "Japan" },

  // L
  { city: "Lagos", name: "Murtala Muhammed International Airport", iata: "LOS", country: "Nigeria" },
  { city: "Lahore", name: "Allama Iqbal International Airport", iata: "LHE", country: "Pakistan" },
  { city: "Las Vegas", name: "Harry Reid International Airport", iata: "LAS", country: "USA" },
  { city: "Lima", name: "Jorge Chávez International Airport", iata: "LIM", country: "Peru" },
  { city: "Lisbon", name: "Humberto Delgado Airport", iata: "LIS", country: "Portugal" },
  { city: "London", name: "Heathrow Airport", iata: "LHR", country: "UK" },
  { city: "London", name: "Gatwick Airport", iata: "LGW", country: "UK" },
  { city: "London", name: "Stansted Airport", iata: "STN", country: "UK" },
  { city: "London", name: "Luton Airport", iata: "LTN", country: "UK" },
  { city: "London", name: "City Airport", iata: "LCY", country: "UK" },
  { city: "Los Angeles", name: "Los Angeles International Airport", iata: "LAX", country: "USA" },
  { city: "Lyon", name: "Lyon–Saint-Exupéry Airport", iata: "LYS", country: "France" },

  // M
  { city: "Madrid", name: "Adolfo Suárez Madrid–Barajas Airport", iata: "MAD", country: "Spain" },
  { city: "Málaga", name: "Málaga Airport", iata: "AGP", country: "Spain" },
  { city: "Male", name: "Velana International Airport", iata: "MLE", country: "Maldives" },
  { city: "Manchester", name: "Manchester Airport", iata: "MAN", country: "UK" },
  { city: "Manila", name: "Ninoy Aquino International Airport", iata: "MNL", country: "Philippines" },
  { city: "Marrakech", name: "Marrakech Menara Airport", iata: "RAK", country: "Morocco" },
  { city: "Marseille", name: "Marseille Provence Airport", iata: "MRS", country: "France" },
  { city: "Medellín", name: "José María Córdova International Airport", iata: "MDE", country: "Colombia" },
  { city: "Melbourne", name: "Melbourne Airport", iata: "MEL", country: "Australia" },
  { city: "Memphis", name: "Memphis International Airport", iata: "MEM", country: "USA" },
  { city: "Mexico City", name: "Benito Juárez International Airport", iata: "MEX", country: "Mexico" },
  { city: "Miami", name: "Miami International Airport", iata: "MIA", country: "USA" },
  { city: "Milan", name: "Malpensa Airport", iata: "MXP", country: "Italy" },
  { city: "Milan", name: "Linate Airport", iata: "LIN", country: "Italy" },
  { city: "Milwaukee", name: "Milwaukee Mitchell International Airport", iata: "MKE", country: "USA" },
  { city: "Minneapolis", name: "Minneapolis-Saint Paul International Airport", iata: "MSP", country: "USA" },
  { city: "Montréal", name: "Montréal-Trudeau International Airport", iata: "YUL", country: "Canada" },
  { city: "Moscow", name: "Sheremetyevo International Airport", iata: "SVO", country: "Russia" },
  { city: "Moscow", name: "Domodedovo International Airport", iata: "DME", country: "Russia" },
  { city: "Mumbai", name: "Chhatrapati Shivaji Maharaj International Airport", iata: "BOM", country: "India" },
  { city: "Munich", name: "Munich Airport", iata: "MUC", country: "Germany" },
  { city: "Muscat", name: "Muscat International Airport", iata: "MCT", country: "Oman" },

  // N
  { city: "Nairobi", name: "Jomo Kenyatta International Airport", iata: "NBO", country: "Kenya" },
  { city: "Nantes", name: "Nantes Atlantique Airport", iata: "NTE", country: "France" },
  { city: "Naples", name: "Naples International Airport", iata: "NAP", country: "Italy" },
  { city: "Nashville", name: "Nashville International Airport", iata: "BNA", country: "USA" },
  { city: "New Orleans", name: "Louis Armstrong New Orleans International Airport", iata: "MSY", country: "USA" },
  { city: "New York", name: "John F. Kennedy International Airport", iata: "JFK", country: "USA" },
  { city: "New York", name: "LaGuardia Airport", iata: "LGA", country: "USA" },
  { city: "Newark", name: "Newark Liberty International Airport", iata: "EWR", country: "USA" },
  { city: "Nice", name: "Nice Côte d'Azur Airport", iata: "NCE", country: "France" },

  // O
  { city: "Oakland", name: "Oakland International Airport", iata: "OAK", country: "USA" },
  { city: "Orlando", name: "Orlando International Airport", iata: "MCO", country: "USA" },
  { city: "Osaka", name: "Kansai International Airport", iata: "KIX", country: "Japan" },
  { city: "Oslo", name: "Oslo Gardermoen Airport", iata: "OSL", country: "Norway" },
  { city: "Ottawa", name: "Ottawa Macdonald–Cartier International Airport", iata: "YOW", country: "Canada" },

  // P
  { city: "Palma de Mallorca", name: "Palma de Mallorca Airport", iata: "PMI", country: "Spain" },
  { city: "Panama City", name: "Tocumen International Airport", iata: "PTY", country: "Panama" },
  { city: "Paris", name: "Charles de Gaulle Airport", iata: "CDG", country: "France" },
  { city: "Paris", name: "Orly Airport", iata: "ORY", country: "France" },
  { city: "Perth", name: "Perth Airport", iata: "PER", country: "Australia" },
  { city: "Philadelphia", name: "Philadelphia International Airport", iata: "PHL", country: "USA" },
  { city: "Phoenix", name: "Phoenix Sky Harbor International Airport", iata: "PHX", country: "USA" },
  { city: "Pittsburgh", name: "Pittsburgh International Airport", iata: "PIT", country: "USA" },
  { city: "Portland", name: "Portland International Airport", iata: "PDX", country: "USA" },
  { city: "Porto", name: "Francisco Sá Carneiro Airport", iata: "OPO", country: "Portugal" },
  { city: "Prague", name: "Václav Havel Airport Prague", iata: "PRG", country: "Czech Republic" },
  { city: "Pune", name: "Pune Airport", iata: "PNQ", country: "India" },
  { city: "Punta Cana", name: "Punta Cana International Airport", iata: "PUJ", country: "Dominican Republic" },

  // Q
  { city: "Quito", name: "Mariscal Sucre International Airport", iata: "UIO", country: "Ecuador" },

  // R
  { city: "Raleigh", name: "Raleigh-Durham International Airport", iata: "RDU", country: "USA" },
  { city: "Reykjavik", name: "Keflavík International Airport", iata: "KEF", country: "Iceland" },
  { city: "Riga", name: "Riga International Airport", iata: "RIX", country: "Latvia" },
  { city: "Rio de Janeiro", name: "Galeão International Airport", iata: "GIG", country: "Brazil" },
  { city: "Riyadh", name: "King Khalid International Airport", iata: "RUH", country: "Saudi Arabia" },
  { city: "Rome", name: "Leonardo da Vinci–Fiumicino Airport", iata: "FCO", country: "Italy" },

  // S
  { city: "Sacramento", name: "Sacramento International Airport", iata: "SMF", country: "USA" },
  { city: "Salt Lake City", name: "Salt Lake City International Airport", iata: "SLC", country: "USA" },
  { city: "San Antonio", name: "San Antonio International Airport", iata: "SAT", country: "USA" },
  { city: "San Diego", name: "San Diego International Airport", iata: "SAN", country: "USA" },
  { city: "San Francisco", name: "San Francisco International Airport", iata: "SFO", country: "USA" },
  { city: "San José", name: "Juan Santamaría International Airport", iata: "SJO", country: "Costa Rica" },
  { city: "San Juan", name: "Luis Muñoz Marín International Airport", iata: "SJU", country: "Puerto Rico" },
  { city: "Santiago", name: "Arturo Merino Benítez International Airport", iata: "SCL", country: "Chile" },
  { city: "São Paulo", name: "São Paulo–Guarulhos International Airport", iata: "GRU", country: "Brazil" },
  { city: "Sapporo", name: "New Chitose Airport", iata: "CTS", country: "Japan" },
  { city: "Seattle", name: "Seattle-Tacoma International Airport", iata: "SEA", country: "USA" },
  { city: "Seoul", name: "Incheon International Airport", iata: "ICN", country: "South Korea" },
  { city: "Seoul", name: "Gimpo International Airport", iata: "GMP", country: "South Korea" },
  { city: "Shanghai", name: "Pudong International Airport", iata: "PVG", country: "China" },
  { city: "Shanghai", name: "Hongqiao International Airport", iata: "SHA", country: "China" },
  { city: "Shenzhen", name: "Shenzhen Bao'an International Airport", iata: "SZX", country: "China" },
  { city: "Singapore", name: "Changi Airport", iata: "SIN", country: "Singapore" },
  { city: "Sofia", name: "Sofia Airport", iata: "SOF", country: "Bulgaria" },
  { city: "St. Louis", name: "St. Louis Lambert International Airport", iata: "STL", country: "USA" },
  { city: "St. Petersburg", name: "Pulkovo Airport", iata: "LED", country: "Russia" },
  { city: "Stockholm", name: "Stockholm Arlanda Airport", iata: "ARN", country: "Sweden" },
  { city: "Sydney", name: "Sydney Airport", iata: "SYD", country: "Australia" },

  // T
  { city: "Taipei", name: "Taiwan Taoyuan International Airport", iata: "TPE", country: "Taiwan" },
  { city: "Tallinn", name: "Lennart Meri Tallinn Airport", iata: "TLL", country: "Estonia" },
  { city: "Tampa", name: "Tampa International Airport", iata: "TPA", country: "USA" },
  { city: "Tehran", name: "Imam Khomeini International Airport", iata: "IKA", country: "Iran" },
  { city: "Tel Aviv", name: "Ben Gurion Airport", iata: "TLV", country: "Israel" },
  { city: "Tenerife", name: "Tenerife South Airport", iata: "TFS", country: "Spain" },
  { city: "Tokyo", name: "Narita International Airport", iata: "NRT", country: "Japan" },
  { city: "Tokyo", name: "Haneda Airport", iata: "HND", country: "Japan" },
  { city: "Toronto", name: "Toronto Pearson International Airport", iata: "YYZ", country: "Canada" },
  { city: "Tunis", name: "Tunis–Carthage International Airport", iata: "TUN", country: "Tunisia" },

  // U
  { city: "Ulaanbaatar", name: "Chinggis Khaan International Airport", iata: "UBN", country: "Mongolia" },

  // V
  { city: "Valencia", name: "Valencia Airport", iata: "VLC", country: "Spain" },
  { city: "Vancouver", name: "Vancouver International Airport", iata: "YVR", country: "Canada" },
  { city: "Venice", name: "Venice Marco Polo Airport", iata: "VCE", country: "Italy" },
  { city: "Vienna", name: "Vienna International Airport", iata: "VIE", country: "Austria" },
  { city: "Vilnius", name: "Vilnius Airport", iata: "VNO", country: "Lithuania" },

  // W
  { city: "Warsaw", name: "Warsaw Chopin Airport", iata: "WAW", country: "Poland" },
  { city: "Washington, D.C.", name: "Dulles International Airport", iata: "IAD", country: "USA" },
  { city: "Washington, D.C.", name: "Ronald Reagan Washington National Airport", iata: "DCA", country: "USA" },
  { city: "Wellington", name: "Wellington Airport", iata: "WLG", country: "New Zealand" },
  { city: "Winnipeg", name: "Winnipeg James Armstrong Richardson International Airport", iata: "YWG", country: "Canada" },

  // Z
  { city: "Zagreb", name: "Franjo Tuđman Airport", iata: "ZAG", country: "Croatia" },
  { city: "Zanzibar", name: "Abeid Amani Karume International Airport", iata: "ZNZ", country: "Tanzania" },
  { city: "Zurich", name: "Zurich Airport", iata: "ZRH", country: "Switzerland" },
];

/**
 * Search airports by city name, airport name, or IATA code.
 * Returns top matches sorted by relevance.
 */
export function searchAirports(query: string, limit = 8): Airport[] {
  const q = query.toLowerCase().trim();
  if (!q) return [];

  // Exact IATA match first
  const exactIata = AIRPORTS.filter((a) => a.iata.toLowerCase() === q);

  // City starts with query
  const cityStartsWith = AIRPORTS.filter(
    (a) =>
      a.city.toLowerCase().startsWith(q) &&
      !exactIata.includes(a)
  );

  // City or airport name contains query
  const contains = AIRPORTS.filter(
    (a) =>
      !exactIata.includes(a) &&
      !cityStartsWith.includes(a) &&
      (a.city.toLowerCase().includes(q) ||
        a.name.toLowerCase().includes(q) ||
        a.iata.toLowerCase().includes(q) ||
        a.country.toLowerCase().includes(q))
  );

  return [...exactIata, ...cityStartsWith, ...contains].slice(0, limit);
}
