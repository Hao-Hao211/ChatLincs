import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  const formData = await req.formData()
  const collectionName = formData.get('collection_name')
  const file = formData.get('file') as File | null

  if (!collectionName) {
    return NextResponse.json({ error: "Please specify a collection name." }, { status: 400 })
  }

  if (!file) {
    return NextResponse.json({ error: "Please upload a file." }, { status: 400 })
  }

  try {
    // Here you would implement the logic to insert the file into the collection
    // For now, we'll just simulate a successful upload
    console.log(`Uploading file ${file.name} to collection ${collectionName}`)

    return NextResponse.json({ message: "Successfully uploaded." }, { status: 200 })
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 })
  }
}

