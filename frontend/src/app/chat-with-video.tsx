"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Loader2, Send, Upload, Youtube, ChevronDown, ChevronUp, User, Bot, HelpCircle } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { cn } from "@/lib/utils"
import { Collapsible, CollapsibleContent } from "@/components/ui/collapsible"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

type ChatMessage = {
  role: "user" | "assistant"
  content: string
  image?: string
}

export function ChatWithVideo() {
  // Video upload state
  const [videoUrl, setVideoUrl] = useState("")
  const [isNoLanguage, setIsNoLanguage] = useState(false)
  const [contextLength, setContextLength] = useState("6")
  const [isUploading, setIsUploading] = useState(false)
  const [isUploadOpen, setIsUploadOpen] = useState(false)

  // Video selection state
  const [videoTitles, setVideoTitles] = useState<string[]>([])
  const [selectedVideo, setSelectedVideo] = useState("")
  const [isLoadingVideos, setIsLoadingVideos] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Chat state
  const [query, setQuery] = useState("")
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isQuerying, setIsQuerying] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const refreshTimerRef = useRef<NodeJS.Timeout | null>(null)
  const { toast } = useToast()

  // Add a ref to track initial load
  const isInitialLoadRef = useRef(true)

  // Fetch all uploaded videos on component mount and set up auto-refresh
  useEffect(() => {
    fetchVideos()

    // Set up auto-refresh every 15 seconds
    refreshTimerRef.current = setInterval(() => {
      setIsRefreshing(true)
      fetchVideos().finally(() => {
        setIsRefreshing(false)
      })
    }, 15000)

    // Clean up interval on component unmount
    return () => {
      if (refreshTimerRef.current) {
        clearInterval(refreshTimerRef.current)
      }
    }
  }, [])

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const fetchVideos = async () => {
    setIsLoadingVideos(true)
    try {
      const response = await fetch("http://127.0.0.1:5000/all_uploaded_videos")
      if (!response.ok) {
        throw new Error("Failed to fetch videos")
      }
      const data = await response.json()
      setVideoTitles(data.video_titles || [])

      // Only set selected video on initial load if none is selected
      if (data.video_titles?.length > 0 && !selectedVideo && isInitialLoadRef.current) {
        setSelectedVideo(data.video_titles[0])
        isInitialLoadRef.current = false
      }

      return data
    } catch (error) {
      console.error("Error fetching videos:", error)
      toast({
        title: "Error",
        description: "Failed to fetch uploaded videos",
        variant: "destructive",
      })
      throw error
    } finally {
      setIsLoadingVideos(false)
    }
  }

  const handleUploadVideo = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!videoUrl.trim()) {
      toast({
        title: "Error",
        description: "Please enter a video URL",
        variant: "destructive",
      })
      return
    }

    setIsUploading(true)

    try {
      const formData = new FormData()
      formData.append("video_url", videoUrl)
      formData.append("video_without_language_sound", isNoLanguage ? "true" : "false")
      formData.append("n", contextLength)

      const response = await fetch("http://127.0.0.1:5000/upload_video", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Failed to upload video")
      }

      const data = await response.json()

      if (data.status === "success") {
        toast({
          title: "Success",
          description: "Video uploaded successfully",
        })

        // Reset form
        setVideoUrl("")
        setIsNoLanguage(false)
        setContextLength("6")
        setIsUploadOpen(false)

        // Refresh video list immediately after upload
        fetchVideos()
      } else {
        throw new Error(data.message || "Unknown error occurred")
      }
    } catch (error) {
      console.error("Error uploading video:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to upload video",
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
    }
  }

  const handleAskQuestion = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!query.trim() || !selectedVideo) {
      toast({
        title: "Error",
        description: "Please enter a question and select a video",
        variant: "destructive",
      })
      return
    }

    // Add user message to chat
    const userMessage: ChatMessage = {
      role: "user",
      content: query,
    }

    setMessages((prev) => [...prev, userMessage])
    setIsQuerying(true)

    try {
      const formData = new FormData()
      formData.append("video_title", selectedVideo)
      formData.append("query", query)

      const response = await fetch("http://127.0.0.1:5000/chat_with_video", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Failed to get response")
      }

      const data = await response.json()

      // Add assistant message to chat
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: data.response,
        image: data.image_base64 ? `data:image/jpeg;base64,${data.image_base64}` : undefined,
      }

      setMessages((prev) => [...prev, assistantMessage])
      setQuery("") // Clear input
    } catch (error) {
      console.error("Error querying video:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to get response",
        variant: "destructive",
      })
    } finally {
      setIsQuerying(false)
    }
  }

  return (
    <TooltipProvider>
      <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
        {/* Header with Video Selection */}
        <div className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm">
          <div className="p-4 max-w-4xl mx-auto">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h2 className="font-semibold text-lg text-gray-800 dark:text-white">Chat With Video</h2>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Ask questions about video content with AI assistance
                </p>
              </div>

              <div className="flex items-center gap-2">
                <div className="flex-1 min-w-[200px] relative">
                  <Select value={selectedVideo} onValueChange={setSelectedVideo}>
                    <SelectTrigger className="w-full bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
                      <SelectValue placeholder="Select a video" />
                      {isRefreshing && (
                        <div className="absolute right-8 top-1/2 transform -translate-y-1/2">
                          <div className="animate-spin h-3 w-3 border-2 border-emerald-500 border-t-transparent rounded-full"></div>
                        </div>
                      )}
                    </SelectTrigger>
                    <SelectContent>
                      {isLoadingVideos ? (
                        <div className="flex items-center justify-center py-2">
                          <Loader2 className="h-4 w-4 animate-spin text-gray-500 dark:text-gray-400" />
                        </div>
                      ) : videoTitles.length === 0 ? (
                        <div className="p-2 text-sm text-gray-500 dark:text-gray-400 text-center">
                          No videos available
                        </div>
                      ) : (
                        videoTitles.map((title) => (
                          <SelectItem key={title} value={title}>
                            {title}
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
                </div>

                <Button variant="outline" className="gap-2" onClick={() => setIsUploadOpen(!isUploadOpen)}>
                  <Upload className="h-4 w-4" />
                  <span className="hidden sm:inline">Upload Video</span>
                  {isUploadOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            {/* Collapsible Upload Form */}
            <Collapsible open={isUploadOpen} onOpenChange={setIsUploadOpen}>
              <CollapsibleContent>
                <div className="mt-4 p-4 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <form onSubmit={handleUploadVideo} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="space-y-2 md:col-span-2">
                        <Label htmlFor="video-url">YouTube URL</Label>
                        <Input
                          id="video-url"
                          value={videoUrl}
                          onChange={(e) => setVideoUrl(e.target.value)}
                          placeholder="https://www.youtube.com/watch?v=..."
                        />
                      </div>

                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <Label htmlFor="context-length">Context Length (n)</Label>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button variant="ghost" size="icon" className="h-6 w-6 p-0">
                                <HelpCircle className="h-4 w-4 text-gray-500" />
                              </Button>
                            </TooltipTrigger>
                            <TooltipContent className="max-w-xs p-4 space-y-2">
                              <p className="font-medium">Transcript Augmentation (n is number of neighboring frames)</p>
                              <ul className="list-disc pl-4 space-y-1 text-sm">
                                <li>
                                  It is advised that we should pick an individual n for each video such that the updated
                                  transcripts say one or two meaningful facts.
                                </li>
                                <li>
                                  Changing the transcriptions which will be ingested into vector store along with their
                                  corresponding frames will affect directly the performance.
                                </li>
                                <li>
                                  It is advised that one needs to do diligent to experiment with one's data to get the
                                  best performance.
                                </li>
                              </ul>
                            </TooltipContent>
                          </Tooltip>
                        </div>
                        <Input
                          id="context-length"
                          type="number"
                          value={contextLength}
                          onChange={(e) => setContextLength(e.target.value)}
                          placeholder="6"
                          min="1"
                        />
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="no-language"
                        checked={isNoLanguage}
                        onCheckedChange={(checked) => setIsNoLanguage(checked === true)}
                      />
                      <Label htmlFor="no-language" className="text-sm">
                        No Language Sound (check for videos without speech)
                      </Label>
                    </div>

                    <div className="flex justify-end">
                      <Button
                        type="submit"
                        className="bg-emerald-500 hover:bg-emerald-600 text-white"
                        disabled={isUploading || !videoUrl.trim()}
                      >
                        {isUploading ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Uploading...
                          </>
                        ) : (
                          <>
                            <Upload className="mr-2 h-4 w-4" />
                            Upload Video
                          </>
                        )}
                      </Button>
                    </div>
                  </form>
                </div>
              </CollapsibleContent>
            </Collapsible>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Chat Messages */}
          <ScrollArea className="flex-1">
            <div className="p-4 max-w-3xl mx-auto">
              <div className="space-y-6">
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-[50vh] text-center space-y-4">
                    <div className="w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                      <Youtube className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <h3 className="text-xl font-medium text-gray-800 dark:text-gray-200">
                      {videoTitles.length === 0
                        ? "Upload a video to get started"
                        : `Ask questions about "${selectedVideo || "the selected video"}"`}
                    </h3>
                    <p className="text-gray-500 dark:text-gray-400 max-w-md">
                      {videoTitles.length === 0
                        ? "Click 'Upload Video' above to add your first video"
                        : "The AI will analyze the video and provide answers with relevant frames"}
                    </p>
                  </div>
                ) : (
                  messages.map((message, i) => (
                    <div
                      key={i}
                      className={cn("flex gap-3", message.role === "user" ? "justify-end" : "justify-start")}
                    >
                      {message.role === "assistant" && (
                        <div className="w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center flex-shrink-0 mt-1">
                          <Bot className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                        </div>
                      )}
                      <div
                        className={cn(
                          "rounded-2xl px-4 py-3 max-w-[85%] shadow-sm",
                          message.role === "user"
                            ? "bg-emerald-500 text-white rounded-tr-none"
                            : "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-tl-none",
                        )}
                      >
                        <p className="whitespace-pre-wrap mb-3 leading-relaxed">{message.content}</p>
                        {message.image && (
                          <div className="mt-2 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                            <img
                              src={message.image || "/placeholder.svg"}
                              alt="Video frame"
                              className="w-full h-auto max-h-[300px] object-contain bg-gray-100 dark:bg-gray-900"
                            />
                            <div className="p-2 text-xs text-gray-500 dark:text-gray-400 flex items-center gap-2">
                              <Youtube className="w-4 h-4" />
                              <span>Frame from {selectedVideo}</span>
                            </div>
                          </div>
                        )}
                      </div>
                      {message.role === "user" && (
                        <div className="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center flex-shrink-0 mt-1">
                          <User className="w-5 h-5 text-white" />
                        </div>
                      )}
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>
          </ScrollArea>

          {/* Chat Input */}
          <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
            <form onSubmit={handleAskQuestion} className="flex gap-2 max-w-3xl mx-auto">
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={
                  !selectedVideo
                    ? "Select a video first..."
                    : videoTitles.length === 0
                      ? "Upload a video to start chatting..."
                      : `Ask about "${selectedVideo}"...`
                }
                className="flex-1"
                disabled={isQuerying || !selectedVideo || videoTitles.length === 0}
              />
              <Button
                type="submit"
                className="bg-emerald-500 hover:bg-emerald-600 text-white"
                disabled={isQuerying || !query.trim() || !selectedVideo || videoTitles.length === 0}
              >
                {isQuerying ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </Button>
            </form>
          </div>
        </div>
      </div>
    </TooltipProvider>
  )
}

