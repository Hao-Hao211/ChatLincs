// 'use client'
//
// import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
// import { Upload, MessageSquare, Map } from 'lucide-react'
// import { ChatInterface } from "./chat-interface"
// import { DocumentUpload } from "./document-upload"
// import { MapPage } from "./map-page"
//
// export default function Home() {
//   return (
//     <div className="flex h-screen">
//       <div className="flex-1 flex flex-col">
//         <Tabs defaultValue="chat" className="flex-1 flex flex-col">
//           <div className="border-b">
//             <div className="flex items-center justify-between px-4 py-2">
//               <div className="flex items-center gap-2">
//                 <img
//                     src="/logo.jpg"
//                     alt="ChatLincs Logo"
//                     className="w-10 h-10 rounded-lg"
//                 />
//                 <div>
//                   <h1 className="font-semibold text-xl">ChatLincs</h1>
//                   <p className="text-sm text-muted-foreground">Multimodal RAG-Driven AI Assistant for Local Ecosystems</p>
//                 </div>
//               </div>
//               <TabsList>
//                 <TabsTrigger value="chat" className="gap-2 transition-all duration-200 ease-in-out hover:bg-muted/80 data-[state=active]:bg-muted">
//                   <MessageSquare className="w-4 h-4" />
//                   Chat
//                 </TabsTrigger>
//                 <TabsTrigger value="map" className="gap-2 transition-all duration-200 ease-in-out hover:bg-muted/80 data-[state=active]:bg-muted">
//                   <Map className="w-4 h-4" />
//                   Map
//                 </TabsTrigger>
//                 <TabsTrigger value="upload" className="gap-2 transition-all duration-200 ease-in-out hover:bg-muted/80 data-[state=active]:bg-muted">
//                   <Upload className="w-4 h-4" />
//                   Upload
//                 </TabsTrigger>
//               </TabsList>
//             </div>
//           </div>
//
//           <div className="flex-1 overflow-hidden">
//             <TabsContent value="chat" className="h-full">
//               <ChatInterface />
//             </TabsContent>
//
//             <TabsContent value="upload" className="h-full">
//               <DocumentUpload />
//             </TabsContent>
//
//             <TabsContent value="map" className="h-full">
//               <MapPage />
//             </TabsContent>
//           </div>
//         </Tabs>
//       </div>
//     </div>
//   )
// }

// "use client"
//
// import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
// import { Upload, MessageSquare, Map, LayoutDashboard } from "lucide-react"
// import { ChatInterface } from "./chat-interface"
// import { DocumentUpload } from "./document-upload"
// import { MapPage } from "./map-page"
// import { EnvironmentalDashboard } from "./environmental-dashboard"
//
// export default function Home() {
//   return (
//     <div className="flex h-screen">
//       <div className="flex-1 flex flex-col">
//         <Tabs defaultValue="chat" className="flex-1 flex flex-col">
//           <div className="border-b">
//             <div className="flex items-center justify-between px-4 py-2">
//               <div className="flex items-center gap-2">
//                 <img src="/logo.jpg" alt="ChatLincs Logo" className="w-10 h-10 rounded-lg" />
//                 <div>
//                   <h1 className="font-semibold text-xl">ChatLincs</h1>
//                   <p className="text-sm text-muted-foreground">
//                     Multimodal RAG-Driven AI Assistant for Local Ecosystems
//                   </p>
//                 </div>
//               </div>
//               <TabsList>
//                 <TabsTrigger
//                   value="chat"
//                   className="gap-2 transition-all duration-200 ease-in-out hover:bg-muted/80 data-[state=active]:bg-muted"
//                 >
//                   <MessageSquare className="w-4 h-4" />
//                   Chat
//                 </TabsTrigger>
//                 <TabsTrigger
//                   value="map"
//                   className="gap-2 transition-all duration-200 ease-in-out hover:bg-muted/80 data-[state=active]:bg-muted"
//                 >
//                   <Map className="w-4 h-4" />
//                   Map
//                 </TabsTrigger>
//                 <TabsTrigger
//                   value="upload"
//                   className="gap-2 transition-all duration-200 ease-in-out hover:bg-muted/80 data-[state=active]:bg-muted"
//                 >
//                   <Upload className="w-4 h-4" />
//                   Upload
//                 </TabsTrigger>
//                 <TabsTrigger
//                   value="dashboard"
//                   className="gap-2 transition-all duration-200 ease-in-out hover:bg-muted/80 data-[state=active]:bg-muted"
//                 >
//                   <LayoutDashboard className="w-4 h-4" />
//                   Dashboard
//                 </TabsTrigger>
//               </TabsList>
//             </div>
//           </div>
//
//           <div className="flex-1 overflow-hidden">
//             <TabsContent value="chat" className="h-full">
//               <ChatInterface />
//             </TabsContent>
//
//             <TabsContent value="upload" className="h-full">
//               <DocumentUpload />
//             </TabsContent>
//
//             <TabsContent value="map" className="h-full">
//               <MapPage />
//             </TabsContent>
//
//             <TabsContent value="dashboard" className="h-full">
//               <EnvironmentalDashboard />
//             </TabsContent>
//           </div>
//         </Tabs>
//       </div>
//     </div>
//   )
// }

// 'use client'
//
// import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
// import { Upload, MessageSquare, Map } from 'lucide-react'
// import { ChatInterface } from "./chat-interface"
// import { DocumentUpload } from "./document-upload"
// import { MapPage } from "./map-page"
//
// export default function Home() {
//   return (
//     <div className="flex h-screen overflow-hidden bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
//       <div className="flex-1 flex flex-col">
//         <Tabs defaultValue="chat" className="flex-1 flex flex-col">
//           <div className="border-b bg-white dark:bg-gray-800 shadow-sm">
//             <div className="flex items-center justify-between px-6 py-4">
//               <div className="flex items-center gap-3">
//                 <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-lg shadow-lg flex items-center justify-center">
//                   <MessageSquare className="w-6 h-6 text-white" />
//                 </div>
//                 <div>
//                   <h1 className="font-bold text-2xl text-gray-800 dark:text-white">Verba</h1>
//                   <p className="text-sm text-gray-500 dark:text-gray-400">AI Assistant</p>
//                 </div>
//               </div>
//               <TabsList className="bg-gray-100 dark:bg-gray-700 p-1 rounded-lg">
//                 <TabsTrigger value="chat" className="data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600 data-[state=active]:text-gray-800 dark:data-[state=active]:text-white rounded-md transition-all duration-200 ease-in-out">
//                   <MessageSquare className="w-4 h-4 mr-2" />
//                   Chat
//                 </TabsTrigger>
//                 <TabsTrigger value="upload" className="data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600 data-[state=active]:text-gray-800 dark:data-[state=active]:text-white rounded-md transition-all duration-200 ease-in-out">
//                   <Upload className="w-4 h-4 mr-2" />
//                   Upload
//                 </TabsTrigger>
//                 <TabsTrigger value="map" className="data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600 data-[state=active]:text-gray-800 dark:data-[state=active]:text-white rounded-md transition-all duration-200 ease-in-out">
//                   <Map className="w-4 h-4 mr-2" />
//                   Map
//                 </TabsTrigger>
//               </TabsList>
//             </div>
//           </div>
//
//           <div className="flex-1 overflow-hidden">
//             <TabsContent value="chat" className="h-full overflow-hidden">
//               <ChatInterface />
//             </TabsContent>
//
//             <TabsContent value="upload" className="h-full overflow-hidden">
//               <DocumentUpload />
//             </TabsContent>
//
//             <TabsContent value="map" className="h-full overflow-hidden">
//               <MapPage />
//             </TabsContent>
//           </div>
//         </Tabs>
//       </div>
//     </div>
//   )
// }

"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Upload, MessageSquare, Map, LayoutDashboard, Video } from "lucide-react"
import { ChatInterface } from "./chat-interface"
import { DocumentUpload } from "./document-upload"
import { MapPage } from "./map-page"
import { EnvironmentalDashboard } from "./environmental-dashboard"
import { ChatWithVideo } from "./chat-with-video"

export default function Home() {
  return (
    <div className="flex h-screen">
      <div className="flex-1 flex flex-col">
        <Tabs defaultValue="chat" className="flex-1 flex flex-col">
          <div className="border-b">
            <div className="flex items-center justify-between px-4 py-2">
              <div className="flex items-center gap-2">
                <img src="/logo.jpg" alt="ChatLincs Logo" className="w-10 h-10 rounded-lg" />
                <div>
                  <h1 className="font-semibold text-xl">ChatLincs</h1>
                  <p className="text-sm text-muted-foreground">
                    Multimodal RAG-Driven AI Assistant for Local Ecosystems
                  </p>
                </div>
              </div>
              <TabsList>
                <TabsTrigger
                  value="chat"
                  className="gap-2 transition-all duration-200 ease-in-out hover:bg-muted/80 data-[state=active]:bg-muted"
                >
                  <MessageSquare className="w-4 h-4" />
                  Chat
                </TabsTrigger>
                <TabsTrigger
                  value="video"
                  className="gap-2 transition-all duration-200 ease-in-out hover:bg-muted/80 data-[state=active]:bg-muted"
                >
                  <Video className="w-4 h-4" />
                  Video
                </TabsTrigger>
                <TabsTrigger
                  value="map"
                  className="gap-2 transition-all duration-200 ease-in-out hover:bg-muted/80 data-[state=active]:bg-muted"
                >
                  <Map className="w-4 h-4" />
                  Map
                </TabsTrigger>
                <TabsTrigger
                  value="upload"
                  className="gap-2 transition-all duration-200 ease-in-out hover:bg-muted/80 data-[state=active]:bg-muted"
                >
                  <Upload className="w-4 h-4" />
                  Upload
                </TabsTrigger>
                <TabsTrigger
                  value="dashboard"
                  className="gap-2 transition-all duration-200 ease-in-out hover:bg-muted/80 data-[state=active]:bg-muted"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  Dashboard
                </TabsTrigger>
              </TabsList>
            </div>
          </div>

          <div className="flex-1 overflow-hidden">
            <TabsContent value="chat" className="h-full">
              <ChatInterface />
            </TabsContent>

            <TabsContent value="video" className="h-full">
              <ChatWithVideo />
            </TabsContent>

            <TabsContent value="upload" className="h-full">
              <DocumentUpload />
            </TabsContent>

            <TabsContent value="map" className="h-full">
              <MapPage />
            </TabsContent>

            <TabsContent value="dashboard" className="h-full">
              <EnvironmentalDashboard />
            </TabsContent>
          </div>
        </Tabs>
      </div>
    </div>
  )
}



