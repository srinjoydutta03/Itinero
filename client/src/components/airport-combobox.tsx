import { useState, useRef, useEffect, useCallback } from "react";
import { searchAirports, type Airport } from "@/lib/airports";
import { MapPin } from "lucide-react";
import { cn } from "@/lib/utils";

interface AirportComboboxProps {
  label: string;
  placeholder: string;
  value: string;
  onSelect: (displayValue: string) => void;
  inline?: boolean;
}

export function AirportCombobox({
  label,
  placeholder,
  value,
  onSelect,
  inline,
}: AirportComboboxProps) {
  const [query, setQuery] = useState(value);
  const [results, setResults] = useState<Airport[]>([]);
  const [open, setOpen] = useState(false);
  const [highlightIndex, setHighlightIndex] = useState(-1);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  // Sync external value changes (e.g. reset form)
  useEffect(() => {
    setQuery(value);
  }, [value]);

  // Search when query changes
  useEffect(() => {
    if (!open) return;
    const matches = searchAirports(query, 8);
    setResults(matches);
    setHighlightIndex(-1);
  }, [query, open]);

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Scroll highlighted item into view
  useEffect(() => {
    if (highlightIndex >= 0 && listRef.current) {
      const item = listRef.current.children[highlightIndex] as HTMLElement;
      item?.scrollIntoView({ block: "nearest" });
    }
  }, [highlightIndex]);

  const selectAirport = useCallback(
    (airport: Airport) => {
      const display = `${airport.city} (${airport.iata})`;
      setQuery(display);
      onSelect(display);
      setOpen(false);
      setResults([]);
    },
    [onSelect]
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    onSelect(e.target.value); // keep parent in sync for free-text
    if (!open) setOpen(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!open || results.length === 0) {
      if (e.key === "ArrowDown" && query.length > 0) {
        setOpen(true);
      }
      return;
    }

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setHighlightIndex((prev) => (prev < results.length - 1 ? prev + 1 : 0));
        break;
      case "ArrowUp":
        e.preventDefault();
        setHighlightIndex((prev) => (prev > 0 ? prev - 1 : results.length - 1));
        break;
      case "Enter":
        e.preventDefault();
        if (highlightIndex >= 0 && results[highlightIndex]) {
          selectAirport(results[highlightIndex]);
        }
        break;
      case "Escape":
        setOpen(false);
        break;
    }
  };

  return (
    <div ref={wrapperRef} className={cn("relative", !inline && "col-span-1 lg:col-span-2")}>
      <div className="relative flex h-14 items-center rounded-xl bg-muted/50 px-4 transition-colors hover:bg-muted/80">
        <MapPin className="mr-3 h-5 w-5 text-muted-foreground" />
        <div className="flex w-full flex-col items-start text-left">
          <label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
            {label}
          </label>
          <input
            ref={inputRef}
            type="text"
            placeholder={placeholder}
            value={query}
            onChange={handleInputChange}
            onFocus={() => { if (query.length > 0) setOpen(true); }}
            onKeyDown={handleKeyDown}
            className="w-full bg-transparent text-sm font-medium text-foreground outline-none placeholder:text-muted-foreground/50"
            required
            autoComplete="off"
          />
        </div>
      </div>

      {/* Dropdown */}
      {open && results.length > 0 && (
        <ul
          ref={listRef}
          className="absolute left-0 right-0 top-[calc(100%+4px)] z-[100] max-h-72 overflow-y-auto rounded-xl border bg-white shadow-xl dark:bg-zinc-900"
        >
          {results.map((airport, i) => (
            <li
              key={airport.iata + airport.city}
              className={cn(
                "flex cursor-pointer items-center gap-3 px-4 py-3 text-sm transition-colors",
                i === highlightIndex
                  ? "bg-primary/10 text-primary"
                  : "hover:bg-muted/60"
              )}
              onMouseDown={(e) => {
                e.preventDefault(); // prevent blur before click fires
                selectAirport(airport);
              }}
              onMouseEnter={() => setHighlightIndex(i)}
            >
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 font-mono text-xs font-bold text-primary">
                {airport.iata}
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{airport.city}</p>
                <p className="truncate text-xs text-muted-foreground">
                  {airport.name} · {airport.country}
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
