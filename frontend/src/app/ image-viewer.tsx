import Image from "next/image"

interface ImageViewerProps {
  url: string
}

export function ImageViewer({ url }: ImageViewerProps) {
  return (
    <div className="w-full aspect-video relative rounded-lg overflow-hidden">
      <Image
        src={url}
        alt="Retrieved content"
        fill
        className="object-cover"
      />
    </div>
  )
}

