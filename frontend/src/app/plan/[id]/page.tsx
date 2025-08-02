"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { MapPinIcon, CalendarIcon, DollarSignIcon, HomeIcon, UtensilsIcon, PlaneIcon } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";

interface StreamingResponse {
  lodging: string;
  food: string;
  travel: string;
  isComplete: boolean;
}

interface Plan {
  location?: string;
  from_date?: string;
  to_date?: string;
  budget?: number;
}

function PlanContent({params} : {params: Promise<{id: string}>}) {
  const [id, setId] = useState<string>("");
  
  useEffect(() => {
    params.then(p => setId(p.id));
  }, [params]);
  const [response, setResponse] = useState<StreamingResponse>({
    lodging: "",
    food: "",
    travel: "",
    isComplete: false
  });

  const [plan, setPlan] = useState<Plan | null>(null);
  
  useEffect(() => {
    if (!id) return;
    
    const fetchPlan = async () => {
      const response = await fetch(`http://localhost:8080/plan/${id}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await response.json();
      setPlan(data);
    };
    fetchPlan();
  }, [id]);

  const location = plan?.location || "paris";
  const dateFrom = plan?.from_date || "";
  const dateTo = plan?.to_date || "";
  const budget = plan?.budget?.toString() || "0";
  
  const formatLocation = (loc: string) => {
    const locations: Record<string, string> = {
      paris: "🇫🇷 Paris, France",
      london: "🇬🇧 London, UK",
      tokyo: "🇯🇵 Tokyo, Japan",
      newyork: "🇺🇸 New York, USA",
      rome: "🇮🇹 Rome, Italy",
      barcelona: "🇪🇸 Barcelona, Spain",
      dubai: "🇦🇪 Dubai, UAE",
      singapore: "🇸🇬 Singapore",
      istanbul: "🇹🇷 Istanbul, Turkiye",
      amsterdam: "🇳🇱 Amsterdam, Netherlands"
    };
    return locations[loc] || loc;
  };

  const fetchRecommendation = async (type: 'lodging' | 'food' | 'travel') => {
    try {
      const response = await fetch(`http://localhost:8080/plan/${id}/recommendation/${type}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      const reader = response.body?.getReader();
      if (!reader) return;

      const decoder = new TextDecoder();
      let content = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        content += decoder.decode(value, { stream: true });
        setResponse(prev => ({ ...prev, [type]: content }));
      }
    } catch (error) {
      setResponse(prev => ({ ...prev, [type]: `Error: ${error}` }));
    }
  };

  useEffect(() => {
    if (!plan) return;
    
    const fetchAllRecommendations = async () => {
      await fetchRecommendation('lodging');
      await fetchRecommendation('food');
      await fetchRecommendation('travel');
      setResponse(prev => ({ ...prev, isComplete: true }));
    };

    fetchAllRecommendations();
  }, [plan, id]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <div className="relative">
          <div className="absolute top-0 right-0">
            <ThemeToggle />
          </div>
          
          <div className="text-center mb-8">
            <Link href="/" className="hover:opacity-80 transition-opacity">
              <div className="flex items-center justify-center mb-4">
                <PlaneIcon className="h-8 w-8 text-blue-600 mr-2" />
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Trip Planner</h1>
              </div>
            </Link>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Plan your perfect journey with AI-powered recommendations tailored to your budget and preferences
            </p>
          </div>

          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPinIcon className="h-5 w-5" />
                Trip Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center gap-2">
                  <MapPinIcon className="h-4 w-4 text-blue-600" />
                  <span className="font-medium">Destination:</span>
                  <Badge variant="secondary">{formatLocation(location)}</Badge>
                </div>
                <div className="flex items-center gap-2">
                  <CalendarIcon className="h-4 w-4 text-green-600" />
                  <span className="font-medium">Dates:</span>
                  <span className="text-sm">{dateFrom} - {dateTo}</span>
                </div>
                <div className="flex items-center gap-2">
                  <DollarSignIcon className="h-4 w-4 text-purple-600" />
                  <span className="font-medium">Budget:</span>
                  <Badge variant="outline">${budget}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <HomeIcon className="h-5 w-5 text-blue-600" />
                  Lodging Recommendations
                  {!response.lodging && <Badge variant="secondary">Generating...</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {response.lodging ? (
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                    {response.lodging}
                    {!response.food && <span className="animate-pulse">|</span>}
                  </p>
                ) : (
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <UtensilsIcon className="h-5 w-5 text-green-600" />
                  Food & Dining
                  {response.lodging && !response.food && <Badge variant="secondary">Generating...</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {response.food ? (
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                    {response.food}
                    {!response.travel && <span className="animate-pulse">|</span>}
                  </p>
                ) : response.lodging ? (
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-2/3" />
                    <Skeleton className="h-4 w-3/4" />
                  </div>
                ) : (
                  <p className="text-gray-500 dark:text-gray-400">Waiting for lodging recommendations...</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PlaneIcon className="h-5 w-5 text-purple-600" />
                  Travel & Transportation
                  {response.food && !response.travel && <Badge variant="secondary">Generating...</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {response.travel ? (
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                    {response.travel}
                    {!response.isComplete && <span className="animate-pulse">|</span>}
                  </p>
                ) : response.food ? (
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-4/5" />
                    <Skeleton className="h-4 w-2/3" />
                  </div>
                ) : (
                  <p className="text-gray-500 dark:text-gray-400">Waiting for food recommendations...</p>
                )}
              </CardContent>
            </Card>
          </div>

          {response.isComplete && (
            <div className="mt-8 text-center">
              <Badge variant="default" className="bg-green-600">
                ✓ Trip plan complete!
              </Badge>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function PlanPage({params}: {params: Promise<{id: string}>}) {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <PlanContent params={params} />
    </Suspense>
  );
}