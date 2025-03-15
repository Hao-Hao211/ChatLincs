// 'use client'
//
// import { Button } from "@/components/ui/button"
// import { Input } from "@/components/ui/input"
// import { ScrollArea } from "@/components/ui/scroll-area"
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
// import { Send } from 'lucide-react'
// import { useState, useEffect } from "react"
// import { RetrievedContent } from "./retrieved-content"
// import { useToast } from "@/hooks/use-toast"
//
// type ChatMessage = {
//   role: 'user' | 'assistant'
//   content: string
// }
//
// type MediaItem = {
//   type: 'image' | 'audio'
//   url: string
// }
//
// export function ChatInterface() {
//   const [messages, setMessages] = useState<ChatMessage[]>([])
//   const [input, setInput] = useState('')
//   const [isLoading, setIsLoading] = useState(false)
//   const [collectionName, setCollectionName] = useState('')
//   const [collections, setCollections] = useState<string[]>([])
//   const [isLoadingCollections, setIsLoadingCollections] = useState(false)
//   const [retrievedMedia, setRetrievedMedia] = useState<MediaItem[]>([])
//   const { toast } = useToast()
//
//   const fetchCollections = async () => {
//     setIsLoadingCollections(true)
//     try {
//       const response = await fetch('http://127.0.0.1:5000/collections')
//       if (!response.ok) {
//         throw new Error('Failed to fetch collections')
//       }
//       const data = await response.json()
//       setCollections(data.collections || [])
//     } catch (error) {
//       console.error('Error fetching collections:', error)
//       toast({
//         title: "Error",
//         description: "Failed to fetch collections",
//         variant: "destructive",
//       })
//     } finally {
//       setIsLoadingCollections(false)
//     }
//   }
//
//   useEffect(() => {
//     fetchCollections()
//   }, [])
//
//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault()
//     if (!input.trim() || isLoading) return
//
//     const userMessage: ChatMessage = { role: 'user', content: input }
//     setMessages(prev => [...prev, userMessage])
//     setInput('')
//     setIsLoading(true)
//     setRetrievedMedia([])
//
//     try {
//       const response = await fetch('http://127.0.0.1:5000/chat', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//           query: input,
//           collection_name: collectionName || null
//         }),
//       })
//
//       if (!response.ok) {
//         throw new Error('Failed to get response from chat API')
//       }
//
//       const data = await response.json()
//       const assistantMessage: ChatMessage = { role: 'assistant', content: data.response }
//       setMessages(prev => [...prev, assistantMessage])
//
//       // Process retrieved media
//       const media: MediaItem[] = []
//       if (data.images) {
//         media.push(...data.images.map((url: string) => ({ type: 'image' as const, url })))
//       }
//       if (data.audio) {
//         media.push(...data.audio.map((url: string) => ({ type: 'audio' as const, url })))
//       }
//       setRetrievedMedia(media)
//     } catch (error) {
//       console.error('Error in chat:', error)
//       toast({
//         title: "Error",
//         description: "Failed to get response from the chat API",
//         variant: "destructive",
//       })
//     } finally {
//       setIsLoading(false)
//     }
//   }
//
//   return (
//     <div className="flex h-full">
//       <div className="flex flex-col w-1/2 border-r">
//         <div className="p-4 border-b">
//           <Select
//             value={collectionName}
//             onValueChange={setCollectionName}
//           >
//             <SelectTrigger className="w-full">
//               <SelectValue placeholder="Select a collection" />
//             </SelectTrigger>
//             <SelectContent>
//               {isLoadingCollections ? (
//                 <div className="flex items-center justify-center py-2">
//                   <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
//                 </div>
//               ) : collections.length === 0 ? (
//                 <div className="p-2 text-sm text-muted-foreground text-center">
//                   No collections available
//                 </div>
//               ) : (
//                 <>
//                   <SelectItem value="all">All Collections</SelectItem>
//                   {collections.map((collection) => (
//                     <SelectItem key={collection} value={collection}>
//                       {collection}
//                     </SelectItem>
//                   ))}
//                 </>
//               )}
//             </SelectContent>
//           </Select>
//         </div>
//         <ScrollArea className="flex-1 p-4">
//           <div className="space-y-4">
//             {messages.map((message, i) => (
//               <div
//                 key={i}
//                 className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
//               >
//                 <div
//                   className={`rounded-lg px-4 py-2 max-w-[80%] ${
//                     message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
//                   }`}
//                 >
//                   <p>{message.content}</p>
//                 </div>
//               </div>
//             ))}
//           </div>
//         </ScrollArea>
//         <form onSubmit={handleSubmit} className="p-4 border-t">
//           <div className="flex gap-2">
//             <Input
//               value={input}
//               onChange={(e) => setInput(e.target.value)}
//               placeholder="Ask a question..."
//               className="flex-1"
//               disabled={isLoading}
//             />
//             <Button
//               type="submit"
//               disabled={isLoading}
//               className="transition-all duration-200 ease-in-out hover:bg-primary/90 active:scale-95"
//             >
//               <Send className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
//             </Button>
//           </div>
//         </form>
//       </div>
//       <RetrievedContent media={retrievedMedia} />
//     </div>
//   )
// }
//

"use client"

import type React from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Send, Upload, X, File, Image, Music, Loader2, FileText, FileIcon as FilePdf, User, Bot } from "lucide-react"
import { useState, useEffect, useRef } from "react"
import { useToast } from "@/hooks/use-toast"
import { cn } from "@/lib/utils"

type ChatMessage = {
  role: "user" | "assistant"
  content: string
  files?: UploadedFile[]
  media?: MediaItem[]
}

type MediaItem = {
  type: "image" | "audio"
  url: string
}

type UploadedFile = {
  name: string
  size: number
  type: string
  file: File
  previewUrl?: string
}

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [collectionName, setCollectionName] = useState("")
  const [collections, setCollections] = useState<string[]>([])
  const [isLoadingCollections, setIsLoadingCollections] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const { toast } = useToast()

  const fetchCollections = async () => {
    setIsLoadingCollections(true)
    try {
      const response = await fetch("http://127.0.0.1:5000/collections")
      if (!response.ok) {
        throw new Error("Failed to fetch collections")
      }
      const data = await response.json()
      setCollections(data.collections || [])
    } catch (error) {
      console.error("Error fetching collections:", error)
      toast({
        title: "Error",
        description: "Failed to fetch collections",
        variant: "destructive",
      })
    } finally {
      setIsLoadingCollections(false)
    }
  }

  useEffect(() => {
    fetchCollections()
  }, [])

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files).map((file) => {
        const fileObj: UploadedFile = {
          name: file.name,
          size: file.size,
          type: file.type,
          file: file,
        }

        // Create preview URLs for images
        if (file.type.startsWith("image/")) {
          fileObj.previewUrl = URL.createObjectURL(file)
        }

        return fileObj
      })
      setUploadedFiles((prev) => [...prev, ...newFiles])
    }
  }

  const removeFile = (index: number) => {
    setUploadedFiles((prev) => {
      const newFiles = [...prev]
      // Revoke object URL to prevent memory leaks
      if (newFiles[index].previewUrl) {
        URL.revokeObjectURL(newFiles[index].previewUrl!)
      }
      newFiles.splice(index, 1)
      return newFiles
    })
  }

  // Clean up object URLs when component unmounts
  useEffect(() => {
    return () => {
      uploadedFiles.forEach((file) => {
        if (file.previewUrl) {
          URL.revokeObjectURL(file.previewUrl)
        }
      })
    }
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if ((!input.trim() && uploadedFiles.length === 0) || isLoading) return

    const userMessage: ChatMessage = {
      role: "user",
      content: input,
      files: uploadedFiles.length > 0 ? [...uploadedFiles] : undefined,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      // Create FormData for file uploads
      const formData = new FormData()
      formData.append("query", input)
      if (collectionName) {
        formData.append("collection_name", collectionName)
      }

      // Add files to FormData
      uploadedFiles.forEach((file, index) => {
        formData.append(`file_${index}`, file.file)
      })

      // For now, we'll keep the original API call format since we're not changing the backend
      // In a real implementation, you would update the backend to handle file uploads
      const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: input,
          collection_name: collectionName || null,
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to get response from chat API")
      }

      const data = await response.json()

      // Process retrieved media
      const media: MediaItem[] = []
      if (data.images) {
        media.push(...data.images.map((url: string) => ({ type: "image" as const, url })))
      }
      if (data.audio) {
        media.push(...data.audio.map((url: string) => ({ type: "audio" as const, url })))
      }

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: data.response,
        media: media.length > 0 ? media : undefined,
      }

      setMessages((prev) => [...prev, assistantMessage])

      // Clear uploaded files after sending
      setUploadedFiles([])
    } catch (error) {
      console.error("Error in chat:", error)
      toast({
        title: "Error",
        description: "Failed to get response from the chat API",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + " B"
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB"
    else return (bytes / 1048576).toFixed(1) + " MB"
  }

  const getFileIcon = (fileType: string) => {
    if (fileType.startsWith("image/")) return <Image className="w-5 h-5" />
    if (fileType.startsWith("audio/")) return <Music className="w-5 h-5" />
    if (fileType.includes("pdf")) return <FilePdf className="w-5 h-5" />
    if (fileType.includes("text")) return <FileText className="w-5 h-5" />
    return <File className="w-5 h-5" />
  }

  return (
    <div className="flex flex-col h-full">
      {/* Fixed Header */}
      <div className="flex-none border-b bg-white dark:bg-gray-800 shadow-sm">
        <div className="p-4 max-w-4xl mx-auto">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-gray-800 dark:text-gray-200">AI Assistant</h2>
            <Select value={collectionName} onValueChange={setCollectionName}>
              <SelectTrigger className="w-[220px] bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
                <SelectValue placeholder="Select a collection" />
              </SelectTrigger>
              <SelectContent>
                {isLoadingCollections ? (
                  <div className="flex items-center justify-center py-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-emerald-500"></div>
                  </div>
                ) : collections.length === 0 ? (
                  <div className="p-2 text-sm text-gray-500 dark:text-gray-400 text-center">
                    No collections available
                  </div>
                ) : (
                  <>
                    <SelectItem value="all">All Collections</SelectItem>
                    {collections.map((collection) => (
                      <SelectItem key={collection} value={collection}>
                        {collection}
                      </SelectItem>
                    ))}
                  </>
                )}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Scrollable Chat Area */}
      <div className="flex-1 overflow-hidden bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-950">
        <ScrollArea className="h-full">
          <div className="p-4 max-w-4xl mx-auto">
            <div className="space-y-6">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-[50vh] text-center space-y-4">
                  <div className="w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                    <Bot className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
                  </div>
                  <h3 className="text-xl font-medium text-gray-800 dark:text-gray-200">How can I help you today?</h3>
                  <p className="text-gray-500 dark:text-gray-400 max-w-md">
                    Ask me anything about your environmental data or upload files for analysis.
                  </p>
                </div>
              ) : (
                messages.map((message, i) => (
                  <div key={i} className={cn("flex gap-3", message.role === "user" ? "justify-end" : "justify-start")}>
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
                      {/* Message content */}
                      {message.content && <p className="whitespace-pre-wrap mb-3 leading-relaxed">{message.content}</p>}

                      {/* Display uploaded files in user messages */}
                      {message.files && message.files.length > 0 && (
                        <div className="space-y-3">
                          {message.files.map((file, fileIndex) => (
                            <div
                              key={fileIndex}
                              className="rounded-lg overflow-hidden transition-all duration-200 hover:shadow-md"
                            >
                              {/* For image files, show the actual image */}
                              {file.type.startsWith("image/") && file.previewUrl ? (
                                <div className="space-y-2">
                                  <div className="rounded-lg overflow-hidden border border-white/20 dark:border-gray-700">
                                    <img
                                      src={file.previewUrl || "/placeholder.svg"}
                                      alt={file.name}
                                      className="w-full h-auto rounded-lg max-h-[300px] object-contain bg-gray-100 dark:bg-gray-900"
                                    />
                                  </div>
                                  <div
                                    className={`flex items-center gap-2 text-xs ${
                                      message.role === "user" ? "text-white/80" : "text-gray-500 dark:text-gray-400"
                                    }`}
                                  >
                                    {getFileIcon(file.type)}
                                    <span>{file.name}</span>
                                    <span>({formatFileSize(file.size)})</span>
                                  </div>
                                </div>
                              ) : (
                                /* For non-image files, show detailed info */
                                <div
                                  className={`flex items-center gap-3 p-3 rounded-lg ${
                                    message.role === "user" ? "bg-emerald-600/40" : "bg-gray-100 dark:bg-gray-700/50"
                                  }`}
                                >
                                  <div
                                    className={`p-3 rounded-lg ${
                                      message.role === "user" ? "bg-emerald-700/40" : "bg-white dark:bg-gray-800"
                                    }`}
                                  >
                                    {getFileIcon(file.type)}
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <p className="font-medium truncate">{file.name}</p>
                                    <p
                                      className={`text-xs ${
                                        message.role === "user" ? "text-white/70" : "text-gray-500 dark:text-gray-400"
                                      }`}
                                    >
                                      {formatFileSize(file.size)} • {file.type.split("/")[1].toUpperCase()}
                                    </p>
                                  </div>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Display retrieved media in assistant messages */}
                      {message.media && message.media.length > 0 && (
                        <div className="mt-3 space-y-4">
                          <div className="flex items-center gap-2 mb-2">
                            <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700"></div>
                            <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                              Retrieved Content
                            </span>
                            <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700"></div>
                          </div>
                          <div className="grid gap-4 grid-cols-1">
                            {message.media.map((item, mediaIndex) => (
                              <div
                                key={mediaIndex}
                                className="rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 shadow-sm transition-all duration-200 hover:shadow-md"
                              >
                                {item.type === "image" ? (
                                  <div className="space-y-2">
                                    <img
                                      src={item.url || "/placeholder.svg"}
                                      alt={`Retrieved image ${mediaIndex + 1}`}
                                      className="w-full h-auto max-h-[300px] object-contain bg-gray-100 dark:bg-gray-900"
                                    />
                                    <div className="p-2 text-xs text-gray-500 dark:text-gray-400 flex items-center gap-2">
                                      <Image className="w-4 h-4" />
                                      <span>Image {mediaIndex + 1}</span>
                                    </div>
                                  </div>
                                ) : (
                                  <div className="p-3">
                                    <div className="flex items-center gap-2 mb-2">
                                      <Music className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                                      <span className="text-sm font-medium">Audio {mediaIndex + 1}</span>
                                    </div>
                                    <audio controls className="w-full">
                                      <source src={item.url} type="audio/mpeg" />
                                      Your browser does not support the audio element.
                                    </audio>
                                  </div>
                                )}
                              </div>
                            ))}
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
      </div>

      {/* Fixed Input Area */}
      <div className="flex-none border-t bg-white dark:bg-gray-800">
        <div className="p-4 max-w-4xl mx-auto">
          {/* File Preview Area */}
          {uploadedFiles.length > 0 && (
            <div className="mb-4">
              <div className="flex items-center gap-2 mb-2">
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Attachments</h3>
                <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700"></div>
              </div>
              <div className="flex flex-wrap gap-2">
                {uploadedFiles.map((file, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full px-3 py-1.5 text-xs group hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200"
                  >
                    <div className="p-1 rounded-full bg-white dark:bg-gray-700">{getFileIcon(file.type)}</div>
                    <span className="truncate max-w-[120px] font-medium">{file.name}</span>
                    <span className="text-gray-500 dark:text-gray-400">({formatFileSize(file.size)})</span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-5 w-5 p-0 rounded-full text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400 opacity-70 group-hover:opacity-100"
                      onClick={() => removeFile(i)}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Input Form */}
          <form onSubmit={handleSubmit} className="flex items-center gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1"
              disabled={isLoading}
            />
            <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" multiple />
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading}
              className="flex-none"
            >
              <Upload className="w-4 h-4" />
            </Button>
            <Button
              type="submit"
              disabled={isLoading || (!input.trim() && uploadedFiles.length === 0)}
              className="flex-none bg-emerald-500 hover:bg-emerald-600 text-white"
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}







