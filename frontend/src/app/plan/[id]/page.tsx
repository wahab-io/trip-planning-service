"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPinIcon, CalendarIcon, DollarSignIcon, HomeIcon, UtensilsIcon, PlaneIcon } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { useTextStream } from "@/components/ui/response-stream";
import { Markdown } from "@/components/ui/markdown";
import { Reasoning, ReasoningContent, ReasoningTrigger } from "@/components/ui/reasoning";

interface StreamingResponse {
  lodging: string;
  food: string;
  travel: string;
  lodgingReasoning: string;
  isReasoningComplete: boolean;
  isComplete: boolean;
}

interface Plan {
  destination?: string;
  from_date?: string;
  to_date?: string;
  budget?: number;
}

function LodgingContent({ content, reasoning, isReasoningComplete }: { content: string; reasoning?: string; isReasoningComplete?: boolean }) {
  const [isStreaming, setIsStreaming] = useState<boolean>(false);

  useEffect(() => {
    if (reasoning && !isReasoningComplete) {
      setIsStreaming(true);
    } else if (isReasoningComplete) {
      setIsStreaming(false);
    }
  }, [reasoning, isReasoningComplete]);

  return (
    <>
      {reasoning && (
          <Reasoning isStreaming={isStreaming}>
            <ReasoningTrigger>Show reasoning</ReasoningTrigger>
            <ReasoningContent className="ml-2 border-l-2 border-l-slate-200 px-2 pb-1 dark:border-l-slate-700" markdown>
              {reasoning}
            </ReasoningContent>
          </Reasoning>
      )}
      <div className="prose dark:prose-invert max-w-none">
        <Markdown>{content}</Markdown>
      </div>
    </>
  );
}

function FoodContent({ content }: { content: string }) {
  const { displayedText } = useTextStream({
    textStream: content,
    speed: 80,
    mode: "fade"
  });


  return (
    <div className="prose dark:prose-invert max-w-none">
      <Markdown>{content}</Markdown>
    </div>
  );
}

function TravelContent({ content }: { content: string }) {
  const { displayedText } = useTextStream({
    textStream: content,
    speed: 80,
    mode: "fade"
  });

  return (
    <div className="prose dark:prose-invert max-w-none">
      <Markdown>{content}</Markdown>
    </div>
  );
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
    lodgingReasoning: "",
    isReasoningComplete: false,
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

  const location = plan?.destination || "paris";
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
      let reasoningContent = '';
      if (type === 'lodging') {
        // Processing lodging with reasoning
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          if (type === 'lodging') {
            setResponse(prev => ({ ...prev, isReasoningComplete: true }));
          }
          break;
        }
        
        const chunk = decoder.decode(value, { stream: true });
        
        if (type === 'lodging') {
          // Parse reasoning and response content
          const fullContent = content + chunk;
          const reasoningMatch = fullContent.match(/<reasoning>([\s\S]*?)<\/reasoning>/g);
          const responseMatch = fullContent.match(/<response>([\s\S]*?)<\/response>/g);
          
          if (reasoningMatch) {
            reasoningContent = reasoningMatch.map(match => match.replace(/<\/?reasoning>/g, '')).join('');
          }
          
          let displayContent = '';
          if (responseMatch) {
            displayContent = responseMatch.map(match => match.replace(/<\/?response>/g, '')).join('');
          } else {
            // If no response tags yet, show content without reasoning tags
            displayContent = fullContent.replace(/<reasoning>[\s\S]*?<\/reasoning>/g, '');
          }
          
          content = fullContent;
          setResponse(prev => ({ 
            ...prev, 
            [type]: displayContent,
            lodgingReasoning: reasoningContent
          }));
        } else {
          content += chunk;
          setResponse(prev => ({ ...prev, [type]: content }));
        }
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
                  <LodgingContent content={response.lodging} reasoning={response.lodgingReasoning} isReasoningComplete={response.isReasoningComplete} />
                ) : (
                  <div className="text-gray-500 dark:text-gray-400">Generating lodging recommendations...</div>
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
                  <FoodContent content={response.food} />
                ) : response.lodging ? (
                  <div className="text-gray-500 dark:text-gray-400">Generating food recommendations...</div>
                ) : (
                  <div className="text-gray-500 dark:text-gray-400">Waiting for lodging recommendations...</div>
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
                  <TravelContent content={response.travel} />
                ) : response.food ? (
                  <div className="text-gray-500 dark:text-gray-400">Generating travel recommendations...</div>
                ) : (
                  <div className="text-gray-500 dark:text-gray-400">Waiting for food recommendations...</div>
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