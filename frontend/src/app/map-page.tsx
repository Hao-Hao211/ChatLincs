'use client'

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { useState, useEffect, useRef } from "react"
import { useToast } from "@/hooks/use-toast"
import { Search } from 'lucide-react'

export function MapPage() {
  const [collections, setCollections] = useState<string[]>([])
  const [isLoadingCollections, setIsLoadingCollections] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [mapHtml, setMapHtml] = useState<string>('')
  const [searchCount, setSearchCount] = useState(0)
  const iframeRef = useRef<HTMLIFrameElement>(null)
  const { toast } = useToast()

  // Form states
  const [collectionName, setCollectionName] = useState('')
  const [address, setAddress] = useState('')
  const [latitude, setLatitude] = useState('')
  const [longitude, setLongitude] = useState('')
  const [keyword, setKeyword] = useState('')
  const [radius, setRadius] = useState(2)

  // Fetch collections on mount
  useEffect(() => {
    const fetchCollections = async () => {
      setIsLoadingCollections(true)
      try {
        const response = await fetch('http://127.0.0.1:5000/collections')
        if (!response.ok) throw new Error('Failed to fetch collections')
        const data = await response.json()
        setCollections(data.collections || [])
      } catch (error) {
        console.error('Error fetching collections:', error)
        toast({
          title: "Error",
          description: "Failed to fetch collections",
          variant: "destructive",
        })
      } finally {
        setIsLoadingCollections(false)
      }
    }
    fetchCollections()
  }, [toast])

  // Update iframe content when mapHtml changes
  useEffect(() => {
    if (iframeRef.current && mapHtml) {
      iframeRef.current.srcdoc = mapHtml
    }
  }, [mapHtml, searchCount])

  const handleSearch = async () => {
    if (!collectionName) {
      toast({
        title: "Error",
        description: "Please select a collection",
        variant: "destructive",
      })
      return
    }

    if (!address && (!latitude || !longitude)) {
      toast({
        title: "Error",
        description: "Please enter either an address or coordinates",
        variant: "destructive",
      })
      return
    }

    setIsSearching(true)

    try {
      const params = new URLSearchParams({
        collection_name: collectionName,
        radius: radius.toString(),
        ...(address ? { address } : {}),
        ...(latitude && longitude ? { lat: latitude, lng: longitude } : {}),
        ...(keyword ? { keyword } : {})
      })

      const response = await fetch(`http://127.0.0.1:5000/geo_map?${params}`)
      if (!response.ok) throw new Error('Search failed')

      const html = await response.text()
      setMapHtml(html)
      setSearchCount(prev => prev + 1) // Increment search count to force re-render
    } catch (error) {
      console.error('Error searching:', error)
      toast({
        title: "Error",
        description: "Search failed. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="flex h-full">
      {/* Left Side - Search Form */}
      <div className="w-1/3 border-r p-6 space-y-6 overflow-y-auto">
        <div>
          <Label htmlFor="collection">Collection Name *</Label>
          <Select
            value={collectionName}
            onValueChange={setCollectionName}
          >
            <SelectTrigger className="w-full mt-1.5">
              <SelectValue placeholder="Select a collection" />
            </SelectTrigger>
            <SelectContent>
              {isLoadingCollections ? (
                <div className="flex items-center justify-center py-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                </div>
              ) : collections.length === 0 ? (
                <div className="p-2 text-sm text-muted-foreground text-center">
                  No collections available
                </div>
              ) : (
                collections.map((collection) => (
                  <SelectItem key={collection} value={collection}>
                    {collection}
                  </SelectItem>
                ))
              )}
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="address">Address</Label>
          <Input
            id="address"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="Enter location address"
            className="mt-1.5"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="latitude">Latitude</Label>
            <Input
              id="latitude"
              type="number"
              value={latitude}
              onChange={(e) => setLatitude(e.target.value)}
              placeholder="Enter latitude"
              className="mt-1.5"
            />
          </div>
          <div>
            <Label htmlFor="longitude">Longitude</Label>
            <Input
              id="longitude"
              type="number"
              value={longitude}
              onChange={(e) => setLongitude(e.target.value)}
              placeholder="Enter longitude"
              className="mt-1.5"
            />
          </div>
        </div>

        <div>
          <Label htmlFor="keyword">Keyword</Label>
          <Input
            id="keyword"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="Filter by keyword"
            className="mt-1.5"
          />
        </div>

        <div>
          <div className="flex justify-between">
            <Label>Search Radius</Label>
            <span className="text-sm text-muted-foreground">{radius} km</span>
          </div>
          <Slider
            value={[radius]}
            onValueChange={([value]) => setRadius(value)}
            min={0.1}
            max={10}
            step={0.1}
            className="mt-3"
          />
        </div>

        <Button
          className="w-full"
          onClick={handleSearch}
          disabled={isSearching}
        >
          {isSearching ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Searching...
            </>
          ) : (
            <>
              <Search className="w-4 h-4 mr-2" />
              Search
            </>
          )}
        </Button>
      </div>

      {/* Right Side - Map Display */}
      <div className="flex-1 h-full">
        {mapHtml ? (
          <iframe
            ref={iframeRef}
            className="w-full h-full border-0"
            sandbox="allow-scripts allow-same-origin"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground bg-muted">
            Search to display map
          </div>
        )}
      </div>
    </div>
  )
}
//
//
// 'use client'
//
// import { Button } from "@/components/ui/button"
// import { Input } from "@/components/ui/input"
// import { Label } from "@/components/ui/label"
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
// import { Slider } from "@/components/ui/slider"
// import { useState, useEffect, useRef } from "react"
// import { useToast } from "@/hooks/use-toast"
// import { Search, Loader2 } from 'lucide-react'
//
// export function MapPage() {
//   const [collections, setCollections] = useState<string[]>([])
//   const [isLoadingCollections, setIsLoadingCollections] = useState(false)
//   const [isSearching, setIsSearching] = useState(false)
//   const [mapHtml, setMapHtml] = useState<string>('')
//   const [searchCount, setSearchCount] = useState(0)
//   const iframeRef = useRef<HTMLIFrameElement>(null)
//   const { toast } = useToast()
//
//   // Form states
//   const [collectionName, setCollectionName] = useState('')
//   const [address, setAddress] = useState('')
//   const [latitude, setLatitude] = useState('')
//   const [longitude, setLongitude] = useState('')
//   const [keyword, setKeyword] = useState('')
//   const [radius, setRadius] = useState(2)
//
//   // Fetch collections on mount
//   useEffect(() => {
//     const fetchCollections = async () => {
//       setIsLoadingCollections(true)
//       try {
//         const response = await fetch('http://127.0.0.1:5000/collections')
//         if (!response.ok) throw new Error('Failed to fetch collections')
//         const data = await response.json()
//         setCollections(data.collections || [])
//       } catch (error) {
//         console.error('Error fetching collections:', error)
//         toast({
//           title: "Error",
//           description: "Failed to fetch collections",
//           variant: "destructive",
//         })
//       } finally {
//         setIsLoadingCollections(false)
//       }
//     }
//     fetchCollections()
//   }, [toast])
//
//   // Update iframe content when mapHtml changes
//   useEffect(() => {
//     if (iframeRef.current && mapHtml) {
//       iframeRef.current.srcdoc = mapHtml
//     }
//   }, [mapHtml, searchCount])
//
//   const handleSearch = async () => {
//     if (!collectionName) {
//       toast({
//         title: "Error",
//         description: "Please select a collection",
//         variant: "destructive",
//       })
//       return
//     }
//
//     if (!address && (!latitude || !longitude)) {
//       toast({
//         title: "Error",
//         description: "Please enter either an address or coordinates",
//         variant: "destructive",
//       })
//       return
//     }
//
//     setIsSearching(true)
//
//     try {
//       const params = new URLSearchParams({
//         collection_name: collectionName,
//         radius: radius.toString(),
//         ...(address ? { address } : {}),
//         ...(latitude && longitude ? { lat: latitude, lng: longitude } : {}),
//         ...(keyword ? { keyword } : {})
//       })
//
//       const response = await fetch(`http://127.0.0.1:5000/geo_map?${params}`)
//       if (!response.ok) throw new Error('Search failed')
//
//       const html = await response.text()
//       setMapHtml(html)
//       setSearchCount(prev => prev + 1) // Increment search count to force re-render
//     } catch (error) {
//       console.error('Error searching:', error)
//       toast({
//         title: "Error",
//         description: "Search failed. Please try again.",
//         variant: "destructive",
//       })
//     } finally {
//       setIsSearching(false)
//     }
//   }
//
//   return (
//     <div className="flex h-full bg-gray-50 dark:bg-gray-900">
//       {/* Left Side - Search Form */}
//       <div className="w-1/3 border-r border-gray-200 dark:border-gray-700 p-6 space-y-6 overflow-y-auto">
//         <div>
//           <Label htmlFor="collection" className="text-sm font-medium text-gray-700 dark:text-gray-300">Collection Name *</Label>
//           <Select
//             value={collectionName}
//             onValueChange={setCollectionName}
//           >
//             <SelectTrigger className="w-full mt-1">
//               <SelectValue placeholder="Select a collection" />
//             </SelectTrigger>
//             <SelectContent>
//               {isLoadingCollections ? (
//                 <div className="flex items-center justify-center py-2">
//                   <Loader2 className="w-4 h-4 animate-spin text-gray-500 dark:text-gray-400" />
//                 </div>
//               ) : collections.length === 0 ? (
//                 <div className="p-2 text-sm text-gray-500 dark:text-gray-400 text-center">
//                   No collections available
//                 </div>
//               ) : (
//                 collections.map((collection) => (
//                   <SelectItem key={collection} value={collection}>
//                     {collection}
//                   </SelectItem>
//                 ))
//               )}
//             </SelectContent>
//           </Select>
//         </div>
//
//         <div>
//           <Label htmlFor="address" className="text-sm font-medium text-gray-700 dark:text-gray-300">Address</Label>
//           <Input
//             id="address"
//             value={address}
//             onChange={(e) => setAddress(e.target.value)}
//             placeholder="Enter location address"
//             className="mt-1"
//           />
//         </div>
//
//         <div className="grid grid-cols-2 gap-4">
//           <div>
//             <Label htmlFor="latitude" className="text-sm font-medium text-gray-700 dark:text-gray-300">Latitude</Label>
//             <Input
//               id="latitude"
//               type="number"
//               value={latitude}
//               onChange={(e) => setLatitude(e.target.value)}
//               placeholder="Enter latitude"
//               className="mt-1"
//             />
//           </div>
//           <div>
//             <Label htmlFor="longitude" className="text-sm font-medium text-gray-700 dark:text-gray-300">Longitude</Label>
//             <Input
//               id="longitude"
//               type="number"
//               value={longitude}
//               onChange={(e) => setLongitude(e.target.value)}
//               placeholder="Enter longitude"
//               className="mt-1"
//             />
//           </div>
//         </div>
//
//         <div>
//           <Label htmlFor="keyword" className="text-sm font-medium text-gray-700 dark:text-gray-300">Keyword</Label>
//           <Input
//             id="keyword"
//             value={keyword}
//             onChange={(e) => setKeyword(e.target.value)}
//             placeholder="Filter by keyword"
//             className="mt-1"
//           />
//         </div>
//
//         <div>
//           <div className="flex justify-between">
//             <Label className="text-sm font-medium text-gray-700 dark:text-gray-300">Search Radius</Label>
//             <span className="text-sm text-gray-500 dark:text-gray-400">{radius} km</span>
//           </div>
//           <Slider
//             value={[radius]}
//             onValueChange={([value]) => setRadius(value)}
//             min={0.1}
//             max={10}
//             step={0.1}
//             className="mt-2"
//           />
//         </div>
//
//         <Button
//           className="w-full bg-emerald-500 hover:bg-emerald-600 text-white transition-all duration-200 ease-in-out"
//           onClick={handleSearch}
//           disabled={isSearching}
//         >
//           {isSearching ? (
//             <>
//               <Loader2 className="w-4 h-4 animate-spin mr-2" />
//               Searching...
//             </>
//           ) : (
//             <>
//               <Search className="w-4 h-4 mr-2" />
//               Search
//             </>
//           )}
//         </Button>
//       </div>
//
//       {/* Right Side - Map Display */}
//       <div className="flex-1 h-full bg-white dark:bg-gray-800">
//         {mapHtml ? (
//           <iframe
//             ref={iframeRef}
//             className="w-full h-full border-0"
//             sandbox="allow-scripts allow-same-origin"
//           />
//         ) : (
//           <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700">
//             Search to display map
//           </div>
//         )}
//       </div>
//     </div>
//   )
// }


