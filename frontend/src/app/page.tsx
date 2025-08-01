"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { MapPinIcon, CalendarIcon, DollarSignIcon, PlaneIcon } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { format } from "date-fns";

const formSchema = z.object({
  location: z.string().min(1, "Please select a destination"),
  dateFrom: z.date({ error: "Start date is required" }),
  dateTo: z.date({ error: "End date is required" }),
  budget: z.number().min(1, "Budget must be greater than 0")
}).refine((data) => data.dateTo > data.dateFrom, {
  message: "End date must be after start date",
  path: ["dateTo"]
});

export default function Home() {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      location: "",
      budget: 0
    }
  });

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsSubmitting(true);
    console.log(values);
    // TODO: Submit to backend
    setTimeout(() => setIsSubmitting(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="relative">
          <div className="absolute top-0 right-0">
            <ThemeToggle />
          </div>
          <div className="text-center mb-12">
            <div className="flex items-center justify-center mb-4">
              <PlaneIcon className="h-12 w-12 text-blue-600 mr-3" />
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white">TripPlanner</h1>
            </div>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Plan your perfect journey with AI-powered recommendations tailored to your budget and preferences
            </p>
          </div>
        </div>

        {/* Trip Planning Form */}
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPinIcon className="h-5 w-5" />
                Plan Your Trip
              </CardTitle>
              <CardDescription>
                Tell us about your dream destination and we&apos;ll create the perfect itinerary for you
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                  {/* Location */}
                  <FormField
                    control={form.control}
                    name="location"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Destination</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select your destination" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="paris">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">🇫🇷</span>
                                Paris, France
                              </div>
                            </SelectItem>
                            <SelectItem value="london">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">🇬🇧</span>
                                London, UK
                              </div>
                            </SelectItem>
                            <SelectItem value="tokyo">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">🇯🇵</span>
                                Tokyo, Japan
                              </div>
                            </SelectItem>
                            <SelectItem value="newyork">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">🇺🇸</span>
                                New York, USA
                              </div>
                            </SelectItem>
                            <SelectItem value="rome">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">🇮🇹</span>
                                Rome, Italy
                              </div>
                            </SelectItem>
                            <SelectItem value="barcelona">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">🇪🇸</span>
                                Barcelona, Spain
                              </div>
                            </SelectItem>
                            <SelectItem value="dubai">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">🇦🇪</span>
                                Dubai, UAE
                              </div>
                            </SelectItem>
                            <SelectItem value="singapore">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">🇸🇬</span>
                                Singapore
                              </div>
                            </SelectItem>
                            <SelectItem value="istanbul">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">🇹🇷</span>
                                Istanbul, Turkey
                              </div>
                            </SelectItem>
                            <SelectItem value="amsterdam">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">🇳🇱</span>
                                Amsterdam, Netherlands
                              </div>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* Date Range */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="dateFrom"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>From Date</FormLabel>
                          <Popover>
                            <PopoverTrigger asChild>
                              <FormControl>
                                <Button
                                  variant="outline"
                                  className={cn(
                                    "w-full pl-3 text-left font-normal",
                                    !field.value && "text-muted-foreground"
                                  )}
                                >
                                  {field.value ? format(field.value, "PPP") : "Pick start date"}
                                  <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                                </Button>
                              </FormControl>
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-0" align="start">
                              <Calendar
                                mode="single"
                                selected={field.value}
                                onSelect={field.onChange}
                                disabled={(date) => date < new Date()}
                              />
                            </PopoverContent>
                          </Popover>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="dateTo"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>To Date</FormLabel>
                          <Popover>
                            <PopoverTrigger asChild>
                              <FormControl>
                                <Button
                                  variant="outline"
                                  className={cn(
                                    "w-full pl-3 text-left font-normal",
                                    !field.value && "text-muted-foreground"
                                  )}
                                >
                                  {field.value ? format(field.value, "PPP") : "Pick end date"}
                                  <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                                </Button>
                              </FormControl>
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-0" align="start">
                              <Calendar
                                mode="single"
                                selected={field.value}
                                onSelect={field.onChange}
                                disabled={(date) => date < new Date()}
                              />
                            </PopoverContent>
                          </Popover>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  {/* Budget */}
                  <FormField
                    control={form.control}
                    name="budget"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Budget (USD)</FormLabel>
                        <FormControl>
                          <div className="relative">
                            <DollarSignIcon className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                            <Input
                              type="number"
                              placeholder="Enter your budget"
                              className="pl-10"
                              {...field}
                              onChange={(e) => field.onChange(Number(e.target.value))}
                            />
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <Button type="submit" className="w-full" disabled={isSubmitting}>
                    {isSubmitting ? "Planning Your Trip..." : "Plan My Trip"}
                  </Button>
                </form>
              </Form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
