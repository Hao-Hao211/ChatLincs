// "use client"
//
// import type React from "react"
// import { useState, useEffect, useRef } from "react"
// import { Button } from "@/components/ui/button"
// import { Input } from "@/components/ui/input"
// import { ScrollArea } from "@/components/ui/scroll-area"
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
// import {
//   Send,
//   Upload,
//   X,
//   File,
//   Image,
//   Music,
//   Loader2,
//   FileText,
//   FileIcon as FilePdf,
//   User,
//   Bot,
//   MoreVertical,
//   Trash,
//   Edit,
// } from "lucide-react"
// import { useToast } from "@/hooks/use-toast"
// import { cn } from "@/lib/utils"
// // 需要先安装 uuid： npm install uuid
// import { v4 as uuidv4 } from "uuid"
// import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
// import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogClose } from "@/components/ui/dialog"
// import { Label } from "@/components/ui/label"
//
// export type ChatMessage = {
//   role: "user" | "assistant"
//   content: string
//   files?: UploadedFile[]
//   media?: MediaItem[]
// }
//
// export type MediaItem = {
//   type: "image" | "audio"
//   url: string
//   transcript?: string
// }
//
// export type UploadedFile = {
//   name: string
//   size: number
//   type: string
//   file: File
//   previewUrl?: string
// }
//
// type Conversation = {
//   sessionId: string
//   title: string // 可显示对话首句或自定义标题
//   messages: ChatMessage[]
// }
//
// export function ChatInterface() {
//   // -------------------- 状态管理 --------------------
//   // 当前对话及历史会话
//   const [conversations, setConversations] = useState<Conversation[]>([])
//   // 当前选中的会话 sessionId
//   const [activeSessionId, setActiveSessionId] = useState<string>("")
//   // 当前对话消息
//   const [messages, setMessages] = useState<ChatMessage[]>([])
//   // 用户输入
//   const [input, setInput] = useState("")
//   const [isLoading, setIsLoading] = useState(false)
//   // 选中的 collection
//   const [collectionName, setCollectionName] = useState("")
//   const [collections, setCollections] = useState<string[]>([])
//   const [isLoadingCollections, setIsLoadingCollections] = useState(false)
//   // 是否检索媒体
//   const [retrieve, setRetrieve] = useState<boolean>(false)
//   // 上传文件，仅支持单文件（可自行扩展）
//   const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
//   const [isRenameDialogOpen, setIsRenameDialogOpen] = useState(false)
//   const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
//   const [newTitle, setNewTitle] = useState("")
//
//   // 引用
//   const fileInputRef = useRef<HTMLInputElement>(null)
//   const messagesEndRef = useRef<HTMLDivElement>(null)
//   const { toast } = useToast()
//
//   // -------------------- 初始化逻辑 --------------------
//   useEffect(() => {
//     createNewConversation()
//     fetchCollections()
//   }, [])
//
//   // 新建对话
//   const createNewConversation = () => {
//     const newSessionId = uuidv4()
//     setActiveSessionId(newSessionId)
//     setMessages([])
//     setConversations((prev) => [{ sessionId: newSessionId, title: "New Chat", messages: [] }, ...prev])
//   }
//
//   // 获取 collections 列表
//   const fetchCollections = async () => {
//     setIsLoadingCollections(true)
//     try {
//       const response = await fetch("http://127.0.0.1:5000/collections")
//       if (!response.ok) {
//         throw new Error("Failed to fetch collections")
//       }
//       const data = await response.json()
//       setCollections(data.collections || [])
//     } catch (error) {
//       console.error("Error fetching collections:", error)
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
//   // 每次消息变化后自动滚动到底部
//   useEffect(() => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
//   }, [messages])
//
//   // -------------------- 文件处理 --------------------
//   const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
//     if (e.target.files) {
//       const newFiles = Array.from(e.target.files).map((file) => {
//         const fileObj: UploadedFile = {
//           name: file.name,
//           size: file.size,
//           type: file.type,
//           file: file,
//         }
//         // 如果是图片，创建预览 URL
//         if (file.type.startsWith("image/")) {
//           fileObj.previewUrl = URL.createObjectURL(file)
//         }
//         return fileObj
//       })
//       setUploadedFiles((prev) => [...prev, ...newFiles])
//     }
//   }
//
//   const removeFile = (index: number) => {
//     setUploadedFiles((prev) => {
//       const newFiles = [...prev]
//       if (newFiles[index].previewUrl) {
//         URL.revokeObjectURL(newFiles[index].previewUrl!)
//       }
//       newFiles.splice(index, 1)
//       return newFiles
//     })
//   }
//
//   // 组件卸载时清理预览 URL
//   useEffect(() => {
//     return () => {
//       uploadedFiles.forEach((file) => {
//         if (file.previewUrl) {
//           URL.revokeObjectURL(file.previewUrl)
//         }
//       })
//     }
//   }, [uploadedFiles])
//
//   // -------------------- 发送消息 --------------------
//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault()
//     // 若输入为空且没有上传文件，或者正在加载，就不发送
//     if ((!input.trim() && uploadedFiles.length === 0) || isLoading) return
//
//     // 先把用户输入保存到本地 state
//     const userMessage: ChatMessage = {
//       role: "user",
//       content: input,
//       files: uploadedFiles.length > 0 ? [...uploadedFiles] : undefined,
//     }
//     setMessages((prev) => [...prev, userMessage])
//     setInput("")
//     setIsLoading(true)
//
//     updateConversationTitle(activeSessionId, userMessage)
//
//     try {
//       // 准备 FormData
//       const formData = new FormData()
//       formData.append("query", input)
//       formData.append("session_id", activeSessionId)
//       if (collectionName) {
//         formData.append("collection_name", collectionName)
//       }
//       formData.append("retrieve", retrieve.toString())
//       // 仅上传第一个文件
//       if (uploadedFiles.length > 0) {
//         formData.append("uploaded_file", uploadedFiles[0].file)
//       }
//
//       // 发请求给后端
//       const response = await fetch("http://127.0.0.1:5000/chat", {
//         method: "POST",
//         body: formData,
//       })
//       if (!response.ok) {
//         throw new Error("Failed to get response from chat API")
//       }
//
//       // 解析后端返回的数据
//       const data = await response.json()
//
//       // 处理返回的媒体
//       const media: MediaItem[] = []
//       // 如果有 images 数组，拼接到 media
//       if (data.images && Array.isArray(data.images)) {
//         media.push(
//           ...data.images.map((url: string) => ({
//             type: "image" as const,
//             url,
//           })),
//         )
//       }
//       // 如果有 audios 数组，拼接到 media
//       if (data.audios && Array.isArray(data.audios)) {
//         // audios 数组中每个元素形如：{ audio: string, transcript: string }
//         media.push(
//           ...data.audios.map((item: { audio: string; transcript: string }) => ({
//             type: "audio" as const,
//             url: item.audio,
//             transcript: item.transcript,
//           })),
//         )
//       }
//
//       // 将后端回复保存为 assistant 消息
//       const assistantMessage: ChatMessage = {
//         role: "assistant",
//         content: data.response,
//         media: media.length > 0 ? media : undefined,
//       }
//       setMessages((prev) => [...prev, assistantMessage])
//
//       // 更新对话列表中的消息
//       setConversations((prev) =>
//         prev.map((conv) =>
//           conv.sessionId === activeSessionId
//             ? { ...conv, messages: [...conv.messages, userMessage, assistantMessage] }
//             : conv,
//         ),
//       )
//
//       // 发送后清空已上传文件
//       setUploadedFiles([])
//     } catch (error) {
//       console.error("Error in chat:", error)
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
//   // -------------------- 工具函数 --------------------
//   const formatFileSize = (bytes: number): string => {
//     if (bytes < 1024) return bytes + " B"
//     else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB"
//     else return (bytes / 1048576).toFixed(1) + " MB"
//   }
//
//   const getFileIcon = (fileType: string) => {
//     if (fileType.startsWith("image/")) return <Image className="w-5 h-5" />
//     if (fileType.startsWith("audio/")) return <Music className="w-5 h-5" />
//     if (fileType.includes("pdf")) return <FilePdf className="w-5 h-5" />
//     if (fileType.includes("text")) return <FileText className="w-5 h-5" />
//     return <File className="w-5 h-5" />
//   }
//
//   // Update conversation title with first three words of first message
//   const updateConversationTitle = (sessionId: string, userMessage: ChatMessage) => {
//     setConversations((prev) =>
//       prev.map((conv) => {
//         if (conv.sessionId === sessionId && conv.title === "New Chat" && userMessage.content) {
//           // Get first three words from user message
//           const words = userMessage.content.trim().split(/\s+/)
//           const firstThreeWords = words.slice(0, 3).join(" ")
//           const newTitle = firstThreeWords.length > 0 ? firstThreeWords : "New Chat"
//           return { ...conv, title: newTitle }
//         }
//         return conv
//       }),
//     )
//   }
//
//   // Delete a conversation
//   const deleteConversation = (sessionId: string) => {
//     setConversations((prev) => prev.filter((conv) => conv.sessionId !== sessionId))
//
//     // If the active conversation is deleted, select another one or create a new one
//     if (sessionId === activeSessionId) {
//       const remainingConversations = conversations.filter((conv) => conv.sessionId !== sessionId)
//       if (remainingConversations.length > 0) {
//         const newActiveSession = remainingConversations[0]
//         setActiveSessionId(newActiveSession.sessionId)
//         setMessages(newActiveSession.messages)
//       } else {
//         createNewConversation()
//       }
//     }
//   }
//
//   // Open rename dialog
//   const openRenameDialog = (conversation: Conversation) => {
//     setSelectedConversation(conversation)
//     setNewTitle(conversation.title)
//     setIsRenameDialogOpen(true)
//   }
//
//   // Rename a conversation
//   const renameConversation = () => {
//     if (!selectedConversation || !newTitle.trim()) return
//
//     setConversations((prev) =>
//       prev.map((conv) =>
//         conv.sessionId === selectedConversation.sessionId ? { ...conv, title: newTitle.trim() } : conv,
//       ),
//     )
//
//     setIsRenameDialogOpen(false)
//   }
//
//   // -------------------- 渲染 --------------------
//   return (
//     <div className="flex h-full">
//       {/* 左侧 Sidebar：显示对话历史及新建对话按钮 */}
//       <aside className="w-64 border-r bg-white dark:bg-gray-800 p-4 overflow-y-auto">
//         <div className="mb-4">
//           <Button onClick={createNewConversation} className="w-full bg-emerald-500 hover:bg-emerald-600 text-white">
//             New Chat
//           </Button>
//         </div>
//         <div>
//           <h3 className="text-lg font-medium mb-2 text-gray-800 dark:text-gray-200">Chat History</h3>
//           {conversations.length === 0 ? (
//             <p className="text-sm text-gray-500">No conversation</p>
//           ) : (
//             <ul className="space-y-2">
//               {conversations.map((conv) => (
//                 <li
//                   key={conv.sessionId}
//                   className={cn(
//                     "p-2 rounded cursor-pointer group flex items-center justify-between",
//                     conv.sessionId === activeSessionId
//                       ? "bg-emerald-100 dark:bg-emerald-900"
//                       : "hover:bg-gray-100 dark:hover:bg-gray-700",
//                   )}
//                 >
//                   <div
//                     className="flex-1 truncate"
//                     onClick={() => {
//                       setActiveSessionId(conv.sessionId)
//                       setMessages(conv.messages)
//                     }}
//                   >
//                     {conv.title}
//                   </div>
//                   <DropdownMenu>
//                     <DropdownMenuTrigger asChild>
//                       <Button variant="ghost" size="icon" className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100">
//                         <MoreVertical className="h-4 w-4" />
//                       </Button>
//                     </DropdownMenuTrigger>
//                     <DropdownMenuContent align="end">
//                       <DropdownMenuItem onClick={() => openRenameDialog(conv)}>
//                         <Edit className="mr-2 h-4 w-4" />
//                         Rename
//                       </DropdownMenuItem>
//                       <DropdownMenuItem
//                         className="text-red-500 focus:text-red-500"
//                         onClick={() => deleteConversation(conv.sessionId)}
//                       >
//                         <Trash className="mr-2 h-4 w-4" />
//                         Delete
//                       </DropdownMenuItem>
//                     </DropdownMenuContent>
//                   </DropdownMenu>
//                 </li>
//               ))}
//             </ul>
//           )}
//         </div>
//       </aside>
//
//       {/* 右侧聊天区域 */}
//       <div className="flex flex-col flex-1">
//         {/* Header */}
//         <div className="flex-none border-b bg-white dark:bg-gray-800 shadow-sm">
//           <div className="p-4 max-w-4xl mx-auto flex items-center justify-between">
//             <h2 className="text-lg font-medium text-gray-800 dark:text-gray-200">AI Assistant</h2>
//             <Select value={collectionName} onValueChange={setCollectionName}>
//               <SelectTrigger className="w-[220px] bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
//                 <SelectValue placeholder="Select a collection" />
//               </SelectTrigger>
//               <SelectContent>
//                 {isLoadingCollections ? (
//                   <div className="flex items-center justify-center py-2">
//                     <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-emerald-500"></div>
//                   </div>
//                 ) : collections.length === 0 ? (
//                   <div className="p-2 text-sm text-gray-500 dark:text-gray-400 text-center">
//                     No collections available
//                   </div>
//                 ) : (
//                   <>
//                     <SelectItem value="all">All Collections</SelectItem>
//                     {collections.map((collection) => (
//                       <SelectItem key={collection} value={collection}>
//                         {collection}
//                       </SelectItem>
//                     ))}
//                   </>
//                 )}
//               </SelectContent>
//             </Select>
//           </div>
//         </div>
//
//         {/* Scrollable Chat Area */}
//         <div className="flex-1 overflow-hidden bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-950">
//           <ScrollArea className="h-full">
//             <div className="p-4 max-w-4xl mx-auto">
//               <div className="space-y-6">
//                 {/* 如果当前没有消息，则显示占位界面 */}
//                 {messages.length === 0 ? (
//                   <div className="flex flex-col items-center justify-center h-[50vh] text-center space-y-4">
//                     <div className="w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
//                       <Bot className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
//                     </div>
//                     <h3 className="text-xl font-medium text-gray-800 dark:text-gray-200">How can I help you today?</h3>
//                     <p className="text-gray-500 dark:text-gray-400 max-w-md">
//                       Ask me anything or upload files for analysis.
//                     </p>
//                   </div>
//                 ) : (
//                   /* 显示对话消息 */
//                   messages.map((message, i) => (
//                     <div
//                       key={i}
//                       className={cn("flex gap-3", message.role === "user" ? "justify-end" : "justify-start")}
//                     >
//                       {message.role === "assistant" && (
//                         <div className="w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center flex-shrink-0 mt-1">
//                           <Bot className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
//                         </div>
//                       )}
//                       <div
//                         className={cn(
//                           "rounded-2xl px-4 py-3 max-w-[85%] shadow-sm",
//                           message.role === "user"
//                             ? "bg-emerald-500 text-white rounded-tr-none"
//                             : "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-tl-none",
//                         )}
//                       >
//                         {/* 文本内容 */}
//                         {message.content && (
//                           <p className="whitespace-pre-wrap mb-3 leading-relaxed">{message.content}</p>
//                         )}
//
//                         {/* 用户上传文件（仅用户消息会有 files） */}
//                         {message.files && message.files.length > 0 && (
//                           <div className="space-y-3">
//                             {message.files.map((file, fileIndex) => (
//                               <div
//                                 key={fileIndex}
//                                 className="rounded-lg overflow-hidden transition-all duration-200 hover:shadow-md"
//                               >
//                                 {file.type.startsWith("image/") && file.previewUrl ? (
//                                   <div className="space-y-2">
//                                     <div className="rounded-lg overflow-hidden border border-white/20 dark:border-gray-700">
//                                       <img
//                                         src={file.previewUrl || "/placeholder.svg"}
//                                         alt={file.name}
//                                         className="w-full h-auto rounded-lg max-h-[300px] object-contain bg-gray-100 dark:bg-gray-900"
//                                       />
//                                     </div>
//                                     <div
//                                       className={cn(
//                                         "flex items-center gap-2 text-xs",
//                                         message.role === "user" ? "text-white/80" : "text-gray-500 dark:text-gray-400",
//                                       )}
//                                     >
//                                       {getFileIcon(file.type)}
//                                       <span>{file.name}</span>
//                                       <span>({formatFileSize(file.size)})</span>
//                                     </div>
//                                   </div>
//                                 ) : (
//                                   <div
//                                     className={cn(
//                                       "flex items-center gap-3 p-3 rounded-lg",
//                                       message.role === "user" ? "bg-emerald-600/40" : "bg-gray-100 dark:bg-gray-700/50",
//                                     )}
//                                   >
//                                     <div
//                                       className={cn(
//                                         "p-3 rounded-lg",
//                                         message.role === "user" ? "bg-emerald-700/40" : "bg-white dark:bg-gray-800",
//                                       )}
//                                     >
//                                       {getFileIcon(file.type)}
//                                     </div>
//                                     <div className="flex-1 min-w-0">
//                                       <p className="font-medium truncate">{file.name}</p>
//                                       <p
//                                         className={cn(
//                                           "text-xs",
//                                           message.role === "user"
//                                             ? "text-white/70"
//                                             : "text-gray-500 dark:text-gray-400",
//                                         )}
//                                       >
//                                         {formatFileSize(file.size)} • {file.type.split("/")[1].toUpperCase()}
//                                       </p>
//                                     </div>
//                                   </div>
//                                 )}
//                               </div>
//                             ))}
//                           </div>
//                         )}
//
//                         {/* 后端返回的媒体内容（assistant 消息中可能带有 images / audios） */}
//                         {message.media && message.media.length > 0 && (
//                           <div className="mt-3 space-y-4">
//                             <div className="flex items-center gap-2 mb-2">
//                               <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700"></div>
//                               <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
//                                 Retrieved Content
//                               </span>
//                               <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700"></div>
//                             </div>
//                             <div className="grid gap-4 grid-cols-1">
//                               {message.media.map((item, mediaIndex) => (
//                                 <div
//                                   key={mediaIndex}
//                                   className="rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 shadow-sm transition-all duration-200 hover:shadow-md"
//                                 >
//                                   {item.type === "image" ? (
//                                     <div className="space-y-2">
//                                       <img
//                                         src={item.url || "/placeholder.svg"}
//                                         alt={`Retrieved image ${mediaIndex + 1}`}
//                                         className="w-full h-auto max-h-[300px] object-contain bg-gray-100 dark:bg-gray-900"
//                                       />
//                                       <div className="p-2 text-xs text-gray-500 dark:text-gray-400 flex items-center gap-2">
//                                         <Image className="w-4 h-4" />
//                                         <span>Image {mediaIndex + 1}</span>
//                                       </div>
//                                     </div>
//                                   ) : (
//                                     <div className="p-3">
//                                       <div className="flex items-center gap-2 mb-2">
//                                         <Music className="w-4 h-4 text-gray-500 dark:text-gray-400" />
//                                         <span className="text-sm font-medium">Audio {mediaIndex + 1}</span>
//                                       </div>
//                                       <audio controls className="w-full">
//                                         <source src={item.url} type="audio/wav" />
//                                         Your browser does not support the audio element.
//                                       </audio>
//                                       {item.transcript && (
//                                         <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
//                                           <strong>Transcript:</strong> {item.transcript}
//                                         </div>
//                                       )}
//                                     </div>
//                                   )}
//                                 </div>
//                               ))}
//                             </div>
//                           </div>
//                         )}
//                       </div>
//                       {message.role === "user" && (
//                         <div className="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center flex-shrink-0 mt-1">
//                           <User className="w-5 h-5 text-white" />
//                         </div>
//                       )}
//                     </div>
//                   ))
//                 )}
//                 <div ref={messagesEndRef} />
//               </div>
//             </div>
//           </ScrollArea>
//         </div>
//
//         {/* 底部输入区 */}
//         <div className="flex-none border-t bg-white dark:bg-gray-800">
//           <div className="p-4 max-w-4xl mx-auto">
//             {/* 上传文件预览 */}
//             {uploadedFiles.length > 0 && (
//               <div className="mb-4">
//                 <div className="flex items-center gap-2 mb-2">
//                   <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Attachments</h3>
//                   <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700"></div>
//                 </div>
//                 <div className="flex flex-wrap gap-2">
//                   {uploadedFiles.map((file, i) => (
//                     <div
//                       key={i}
//                       className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full px-3 py-1.5 text-xs group hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200"
//                     >
//                       <div className="p-1 rounded-full bg-white dark:bg-gray-700">{getFileIcon(file.type)}</div>
//                       <span className="truncate max-w-[120px] font-medium">{file.name}</span>
//                       <span className="text-gray-500 dark:text-gray-400">({formatFileSize(file.size)})</span>
//                       <Button
//                         variant="ghost"
//                         size="icon"
//                         className="h-5 w-5 p-0 rounded-full text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400 opacity-70 group-hover:opacity-100"
//                         onClick={() => removeFile(i)}
//                       >
//                         <X className="h-3 w-3" />
//                       </Button>
//                     </div>
//                   ))}
//                 </div>
//               </div>
//             )}
//
//             {/* 输入框 & 按钮 */}
//             <form onSubmit={handleSubmit} className="flex items-center gap-2">
//               <Input
//                 value={input}
//                 onChange={(e) => setInput(e.target.value)}
//                 placeholder="Type your message..."
//                 className="flex-1"
//                 disabled={isLoading}
//               />
//               <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" multiple />
//               <Button
//                 type="button"
//                 variant="outline"
//                 size="icon"
//                 onClick={() => fileInputRef.current?.click()}
//                 disabled={isLoading}
//                 className="flex-none"
//               >
//                 <Upload className="w-4 h-4" />
//               </Button>
//               {/* Retrieve 开关按钮 */}
//               <Button
//                 type="button"
//                 variant={retrieve ? "default" : "outline"}
//                 onClick={() => setRetrieve(!retrieve)}
//                 disabled={isLoading}
//                 className="flex-none"
//               >
//                 {retrieve ? "Retrieve ON" : "Retrieve OFF"}
//               </Button>
//               <Button
//                 type="submit"
//                 disabled={isLoading || (!input.trim() && uploadedFiles.length === 0)}
//                 className="flex-none bg-emerald-500 hover:bg-emerald-600 text-white"
//               >
//                 {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
//               </Button>
//             </form>
//           </div>
//         </div>
//       </div>
//       {/* Rename Dialog */}
//       <Dialog open={isRenameDialogOpen} onOpenChange={setIsRenameDialogOpen}>
//         <DialogContent className="sm:max-w-md">
//           <DialogHeader>
//             <DialogTitle>Rename Conversation</DialogTitle>
//           </DialogHeader>
//           <div className="grid gap-4 py-4">
//             <div className="grid grid-cols-4 items-center gap-4">
//               <Label htmlFor="name" className="text-right">
//                 Name
//               </Label>
//               <Input
//                 id="name"
//                 value={newTitle}
//                 onChange={(e) => setNewTitle(e.target.value)}
//                 className="col-span-3"
//                 autoFocus
//               />
//             </div>
//           </div>
//           <DialogFooter>
//             <DialogClose asChild>
//               <Button variant="outline">Cancel</Button>
//             </DialogClose>
//             <Button onClick={renameConversation} disabled={!newTitle.trim()}>
//               Save
//             </Button>
//           </DialogFooter>
//         </DialogContent>
//       </Dialog>
//     </div>
//   )
// }
//
"use client"

import type React from "react"
import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Send,
  Upload,
  X,
  File,
  Image,
  Music,
  Loader2,
  FileText,
  FileIcon as FilePdf,
  User,
  Bot,
  MoreVertical,
  Trash,
  Edit,
  Check,
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { cn } from "@/lib/utils"
// 需要先安装 uuid： npm install uuid
import { v4 as uuidv4 } from "uuid"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Checkbox } from "@/components/ui/checkbox"

export type ChatMessage = {
  role: "user" | "assistant"
  content: string
  files?: UploadedFile[]
  media?: MediaItem[]
}

export type MediaItem = {
  type: "image" | "audio"
  url: string
  transcript?: string
}

export type UploadedFile = {
  name: string
  size: number
  type: string
  file: File
  previewUrl?: string
}

type Conversation = {
  sessionId: string
  title: string // 可显示对话首句或自定义标题
  messages: ChatMessage[]
}

// Storage keys
const STORAGE_KEYS = {
  CONVERSATIONS: "chatlincs-conversations",
  ACTIVE_SESSION: "chatlincs-active-session",
}

export function ChatInterface() {
  // -------------------- 状态管理 --------------------
  // 当前对话及历史会话
  const [conversations, setConversations] = useState<Conversation[]>([])
  // 当前选中的会话 sessionId
  const [activeSessionId, setActiveSessionId] = useState<string>("")
  // 当前对话消息
  const [messages, setMessages] = useState<ChatMessage[]>([])
  // 用户输入
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  // 选中的 collection
  const [collectionName, setCollectionName] = useState("")
  const [collections, setCollections] = useState<string[]>([])
  const [isLoadingCollections, setIsLoadingCollections] = useState(false)
  // 是否检索媒体
  const [retrieve, setRetrieve] = useState<boolean>(false)
  // 上传文件，仅支持单文件（可自行扩展）
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  // Add this after the other state declarations
  const [collectionError, setCollectionError] = useState(false)
  // Initialization flag
  const [isInitialized, setIsInitialized] = useState(false)

  // Inline editing state
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null)
  const [editingTitle, setEditingTitle] = useState("")

  // 引用
  const fileInputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const editInputRef = useRef<HTMLInputElement>(null)
  const { toast } = useToast()

  // -------------------- 初始化逻辑 --------------------
  useEffect(() => {
    // Load conversations from localStorage
    const loadSavedData = () => {
      try {
        // Load conversations
        const savedConversations = localStorage.getItem(STORAGE_KEYS.CONVERSATIONS)
        const parsedConversations = savedConversations ? JSON.parse(savedConversations) : []

        // Load active session
        const savedActiveSession = localStorage.getItem(STORAGE_KEYS.ACTIVE_SESSION)

        if (parsedConversations.length > 0) {
          setConversations(parsedConversations)

          // Set active session
          const sessionToActivate = savedActiveSession || parsedConversations[0].sessionId
          setActiveSessionId(sessionToActivate)

          // Set messages for active session
          const activeConversation = parsedConversations.find(
            (conv: Conversation) => conv.sessionId === sessionToActivate,
          )
          if (activeConversation) {
            setMessages(activeConversation.messages)
          }
        } else {
          // If no conversations, create a new one
          createNewConversation()
        }
      } catch (error) {
        console.error("Error loading saved conversations:", error)
        createNewConversation()
      }

      setIsInitialized(true)
    }

    loadSavedData()
    fetchCollections()
  }, [])

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    if (isInitialized && conversations.length > 0) {
      localStorage.setItem(STORAGE_KEYS.CONVERSATIONS, JSON.stringify(conversations))
    }
  }, [conversations, isInitialized])

  // Save active session to localStorage whenever it changes
  useEffect(() => {
    if (isInitialized && activeSessionId) {
      localStorage.setItem(STORAGE_KEYS.ACTIVE_SESSION, activeSessionId)
    }
  }, [activeSessionId, isInitialized])

  // Focus edit input when editing starts
  useEffect(() => {
    if (editingSessionId && editInputRef.current) {
      editInputRef.current.focus()
    }
  }, [editingSessionId])

  // 新建对话
  const createNewConversation = () => {
    const newSessionId = uuidv4()
    setActiveSessionId(newSessionId)
    setMessages([])
    setConversations((prev) => [{ sessionId: newSessionId, title: "New Chat", messages: [] }, ...prev])
  }

  // 获取 collections 列表
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

  // 每次消息变化后自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // -------------------- 文件处理 --------------------
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files).map((file) => {
        const fileObj: UploadedFile = {
          name: file.name,
          size: file.size,
          type: file.type,
          file: file,
        }
        // 如果是图片，创建预览 URL
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
      if (newFiles[index].previewUrl) {
        URL.revokeObjectURL(newFiles[index].previewUrl!)
      }
      newFiles.splice(index, 1)
      return newFiles
    })
  }

  // 组件卸载时清理预览 URL
  useEffect(() => {
    return () => {
      uploadedFiles.forEach((file) => {
        if (file.previewUrl) {
          URL.revokeObjectURL(file.previewUrl)
        }
      })
    }
  }, [uploadedFiles])

  // Add this effect after the other useEffect hooks
  useEffect(() => {
    // 当用户选择了collection或取消勾选retrieve时，清除错误提示
    if (collectionName || !retrieve) {
      setCollectionError(false)
    }
  }, [collectionName, retrieve])

  // -------------------- 发送消息 --------------------
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    // 若输入为空或者正在加载，就不发送
    if (!input.trim() || isLoading) return

    // 验证：如果勾选了retrieve但没有选择collection，显示错误提示
    if (retrieve && (!collectionName || collectionName === "")) {
      setCollectionError(true)
      return
    }

    // 先把用户输入保存到本地 state
    const userMessage: ChatMessage = {
      role: "user",
      content: input,
      files: uploadedFiles.length > 0 ? [...uploadedFiles] : undefined,
    }
    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    updateConversationTitle(activeSessionId, userMessage)

    try {
      // 准备 FormData
      const formData = new FormData()
      formData.append("query", input)
      formData.append("session_id", activeSessionId)
      if (collectionName) {
        formData.append("collection_name", collectionName)
      }
      formData.append("retrieve", retrieve.toString())
      // 仅上传第一个文件
      if (uploadedFiles.length > 0) {
        formData.append("uploaded_file", uploadedFiles[0].file)
      }

      // 发请求给后端
      const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        body: formData,
      })
      if (!response.ok) {
        throw new Error("Failed to get response from chat API")
      }

      // 解析后端返回的数据
      const data = await response.json()

      // 处理返回的媒体
      const media: MediaItem[] = []
      // 如果有 images 数组，拼接到 media
      if (data.images && Array.isArray(data.images)) {
        media.push(
          ...data.images.map((url: string) => ({
            type: "image" as const,
            url,
          })),
        )
      }
      // 如果有 audios 数组，拼接到 media
      if (data.audios && Array.isArray(data.audios)) {
        // audios 数组中每个元素形如：{ audio: string, transcript: string }
        media.push(
          ...data.audios.map((item: { audio: string; transcript: string }) => ({
            type: "audio" as const,
            url: item.audio,
            transcript: item.transcript,
          })),
        )
      }

      // 将后端回复保存为 assistant 消息
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: data.response,
        media: media.length > 0 ? media : undefined,
      }
      setMessages((prev) => [...prev, assistantMessage])

      // 更新对话列表中的消息
      setConversations((prev) =>
        prev.map((conv) =>
          conv.sessionId === activeSessionId
            ? { ...conv, messages: [...conv.messages, userMessage, assistantMessage] }
            : conv,
        ),
      )

      // 发送后清空已上传文件
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

  // -------------------- 工具函数 --------------------
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

  // Update conversation title with first three words of first message
  const updateConversationTitle = (sessionId: string, userMessage: ChatMessage) => {
    setConversations((prev) =>
      prev.map((conv) => {
        if (conv.sessionId === sessionId && conv.title === "New Chat" && userMessage.content) {
          // Get first three words from user message
          const words = userMessage.content.trim().split(/\s+/)
          const firstThreeWords = words.slice(0, 3).join(" ")
          const newTitle = firstThreeWords.length > 0 ? firstThreeWords : "New Chat"
          return { ...conv, title: newTitle }
        }
        return conv
      }),
    )
  }

  // Delete a conversation
  const deleteConversation = (sessionId: string) => {
    setConversations((prev) => prev.filter((conv) => conv.sessionId !== sessionId))

    // If the active conversation is deleted, select another one or create a new one
    if (sessionId === activeSessionId) {
      const remainingConversations = conversations.filter((conv) => conv.sessionId !== sessionId)
      if (remainingConversations.length > 0) {
        const newActiveSession = remainingConversations[0]
        setActiveSessionId(newActiveSession.sessionId)
        setMessages(newActiveSession.messages)
      } else {
        createNewConversation()
      }
    }
  }

  // Start editing a conversation title
  const startEditing = (sessionId: string, currentTitle: string) => {
    setEditingSessionId(sessionId)
    setEditingTitle(currentTitle)
  }

  // Save the edited title
  const saveEditedTitle = () => {
    if (!editingSessionId || !editingTitle.trim()) {
      setEditingSessionId(null)
      return
    }

    // Create a new conversations array with the updated title
    const updatedConversations = conversations.map((conv) =>
      conv.sessionId === editingSessionId ? { ...conv, title: editingTitle.trim() } : conv,
    )

    // Update the state with the new array
    setConversations(updatedConversations)

    // Reset editing state
    setEditingSessionId(null)
    setEditingTitle("")
  }

  // Handle key press in the edit input
  const handleEditKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      saveEditedTitle()
    } else if (e.key === "Escape") {
      setEditingSessionId(null)
      setEditingTitle("")
    }
  }

  // -------------------- 渲染 --------------------
  return (
    <div className="flex h-full">
      {/* 左侧 Sidebar：显示对话历史及新建对话按钮 */}
      <aside className="w-64 border-r bg-white dark:bg-gray-800 p-4 overflow-y-auto">
        <div className="mb-4">
          <Button onClick={createNewConversation} className="w-full bg-emerald-500 hover:bg-emerald-600 text-white">
            New Chat
          </Button>
        </div>
        <div>
          <h3 className="text-lg font-medium mb-2 text-gray-800 dark:text-gray-200">Chat History</h3>
          {conversations.length === 0 ? (
            <p className="text-sm text-gray-500">暂无对话</p>
          ) : (
            <ul className="space-y-2">
              {conversations.map((conv) => (
                <li
                  key={conv.sessionId}
                  className={cn(
                    "p-2 rounded cursor-pointer group flex items-center justify-between",
                    conv.sessionId === activeSessionId
                      ? "bg-emerald-100 dark:bg-emerald-900"
                      : "hover:bg-gray-100 dark:hover:bg-gray-700",
                  )}
                >
                  {editingSessionId === conv.sessionId ? (
                    <div className="flex-1 flex items-center gap-2">
                      <Input
                        ref={editInputRef}
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onKeyDown={handleEditKeyPress}
                        className="flex-1 h-7 py-1"
                        autoFocus
                      />
                      <Button variant="ghost" size="icon" className="h-7 w-7 p-0" onClick={saveEditedTitle}>
                        <Check className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <>
                      <div
                        className="flex-1 truncate"
                        onClick={() => {
                          setActiveSessionId(conv.sessionId)
                          setMessages(conv.messages)
                        }}
                      >
                        {conv.title}
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => startEditing(conv.sessionId, conv.title)}>
                            <Edit className="mr-2 h-4 w-4" />
                            Rename
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-red-500 focus:text-red-500"
                            onClick={() => deleteConversation(conv.sessionId)}
                          >
                            <Trash className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </aside>

      {/* 右侧聊天区域 - 使用固定布局 */}
      <div className="flex-1 relative h-full overflow-hidden">
        {/* Header - Fixed at top */}
        <div className="absolute top-0 left-0 right-0 z-10 border-b bg-white dark:bg-gray-800 shadow-sm">
          <div className="p-4 max-w-4xl mx-auto flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-lg text-gray-800 dark:text-white">Multimodal RAG</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
                  Ask questions and retrieve insights from image, text, and audio
            </p>
            </div>
            <Select
              value={collectionName}
              onValueChange={setCollectionName}
              onOpenChange={() => {
                if (collectionError) setCollectionError(false)
              }}
            >
              <div className="relative">
                <SelectTrigger
                  className={cn(
                    "w-[220px] bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700",
                    collectionError && "border-red-500 ring-1 ring-red-500",
                  )}
                >
                  <SelectValue placeholder="Select a collection" />
                </SelectTrigger>
                {collectionError && (
                  <div className="absolute -bottom-10 left-0 right-0 bg-red-500 text-white text-xs p-2 rounded shadow-md z-50">
                    Please select a collection when Retrieve is enabled
                  </div>
                )}
              </div>
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

        {/* Scrollable Chat Area - Fixed position with top and bottom offsets */}
        <div className="absolute top-[64px] bottom-[140px] left-0 right-0 overflow-auto bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-950">
          <div className="p-4 max-w-4xl mx-auto">
            <div className="space-y-6">
              {/* 如果当前没有消息，则显示占位界面 */}
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-[50vh] text-center space-y-4">
                  <div className="w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                    <Bot className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
                  </div>
                  <h3 className="text-xl font-medium text-gray-800 dark:text-gray-200">How can I help you today?</h3>
                  <p className="text-gray-500 dark:text-gray-400 max-w-md">
                    Ask me anything or upload files for analysis.
                  </p>
                </div>
              ) : (
                /* 显示对话消息 */
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
                      {/* 文本内容 */}
                      {message.content && <p className="whitespace-pre-wrap mb-3 leading-relaxed">{message.content}</p>}

                      {/* 用户上传文件（仅用户消息会有 files） */}
                      {message.files && message.files.length > 0 && (
                        <div className="space-y-3">
                          {message.files.map((file, fileIndex) => (
                            <div
                              key={fileIndex}
                              className="rounded-lg overflow-hidden transition-all duration-200 hover:shadow-md"
                            >
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
                                    className={cn(
                                      "flex items-center gap-2 text-xs",
                                      message.role === "user" ? "text-white/80" : "text-gray-500 dark:text-gray-400",
                                    )}
                                  >
                                    {getFileIcon(file.type)}
                                    <span>{file.name}</span>
                                    <span>({formatFileSize(file.size)})</span>
                                  </div>
                                </div>
                              ) : (
                                <div
                                  className={cn(
                                    "flex items-center gap-3 p-3 rounded-lg",
                                    message.role === "user" ? "bg-emerald-600/40" : "bg-gray-100 dark:bg-gray-700/50",
                                  )}
                                >
                                  <div
                                    className={cn(
                                      "p-3 rounded-lg",
                                      message.role === "user" ? "bg-emerald-700/40" : "bg-white dark:bg-gray-800",
                                    )}
                                  >
                                    {getFileIcon(file.type)}
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <p className="font-medium truncate">{file.name}</p>
                                    <p
                                      className={cn(
                                        "text-xs",
                                        message.role === "user" ? "text-white/70" : "text-gray-500 dark:text-gray-400",
                                      )}
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

                      {/* 后端返回的媒体内容（assistant 消息中可能带有 images / audios） */}
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
                                      <source src={item.url} type="audio/wav" />
                                      Your browser does not support the audio element.
                                    </audio>
                                    {item.transcript && (
                                      <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                                        <strong>Transcript:</strong> {item.transcript}
                                      </div>
                                    )}
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
        </div>

        {/* 底部输入区 - Fixed at bottom */}
        <div className="absolute bottom-0 left-0 right-0 z-10 border-t bg-white dark:bg-gray-800">
          <div className="p-4 max-w-4xl mx-auto">
            {/* 上传文件预览 */}
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

            {/* 输入框 & 按钮 */}
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
              {/* Retrieve checkbox */}
              <div className="flex items-center gap-2">
                <Checkbox
                  id="retrieve"
                  checked={retrieve}
                  onCheckedChange={(checked) => {
                    setRetrieve(!!checked)
                    if (!checked) setCollectionError(false)
                  }}
                  disabled={isLoading}
                />
                <label
                  htmlFor="retrieve"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                >
                  Retrieve
                </label>
              </div>
              <Button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="flex-none bg-emerald-500 hover:bg-emerald-600 text-white"
              >
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}











