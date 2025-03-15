import { ScrollArea } from "@/components/ui/scroll-area"
import { Image, Music } from 'lucide-react'

type MediaItem = {
  type: 'image' | 'audio'
  url: string
}

type RetrievedContentProps = {
  media?: MediaItem[]
}

export function RetrievedContent({ media = [] }: RetrievedContentProps) {
  return (
    <div className="flex flex-col h-full w-1/2">
      <div className="border-b p-4">
        <h2 className="font-semibold">Retrieved Content</h2>
        <p className="text-sm text-muted-foreground">
          {media.length} item{media.length !== 1 ? 's' : ''} found
        </p>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {media.map((item, index) => (
            <div key={index} className="border rounded-lg overflow-hidden">
              <div className="border-b p-3 bg-muted/50">
                <div className="flex items-center gap-2">
                  {item.type === 'image' ? (
                    <Image className="w-4 h-4" />
                  ) : (
                    <Music className="w-4 h-4" />
                  )}
                  <span className="font-medium">
                    {item.type === 'image' ? 'Image' : 'Audio'} {index + 1}
                  </span>
                </div>
              </div>
              <div className="p-4">
                {item.type === 'image' ? (
                  <img
                    src={item.url || "/placeholder.svg"}
                    alt={`Retrieved content ${index + 1}`}
                    className="w-full h-auto rounded-lg"
                  />
                ) : (
                  <audio controls className="w-full">
                    <source src={item.url} type="audio/mpeg" />
                    Your browser does not support the audio element.
                  </audio>
                )}
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  )
}

