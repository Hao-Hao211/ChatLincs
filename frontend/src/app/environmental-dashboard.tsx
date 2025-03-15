"use client"

import { useState } from "react"
import { DragDropContext, Droppable, Draggable, type DropResult } from "@hello-pangea/dnd"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Plus, Calendar, Users, Edit, Trash2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

type Task = {
  id: string
  title: string
  description: string
  status: "todo" | "inProgress" | "done"
  priority: "low" | "medium" | "high"
  dueDate: string
  assignee: string
  category: string
  isCompleted: boolean
}

const initialTasks: Task[] = [
  {
    id: "1",
    title: "Organize beach cleanup",
    description: "Plan and execute a beach cleanup event",
    status: "todo",
    priority: "high",
    dueDate: "2023-08-15",
    assignee: "John Doe",
    category: "Pollution Control",
    isCompleted: false,
  },
  {
    id: "2",
    title: "Plant trees in local park",
    description: "Coordinate with local authorities to plant trees",
    status: "inProgress",
    priority: "medium",
    dueDate: "2023-09-01",
    assignee: "Jane Smith",
    category: "Reforestation",
    isCompleted: false,
  },
  {
    id: "3",
    title: "Conduct wildlife survey",
    description: "Perform a survey of local wildlife population",
    status: "done",
    priority: "low",
    dueDate: "2023-07-30",
    assignee: "Alex Johnson",
    category: "Wildlife Conservation",
    isCompleted: true,
  },
]

export function EnvironmentalDashboard() {
  const [tasks, setTasks] = useState<Task[]>(initialTasks)
  const [newTask, setNewTask] = useState<Partial<Task>>({
    title: "",
    description: "",
    priority: "medium",
    category: "",
    dueDate: "",
    assignee: "",
    isCompleted: false,
  })
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [isAddTaskModalOpen, setIsAddTaskModalOpen] = useState(false)
  const { toast } = useToast()

  const onDragEnd = (result: DropResult) => {
    const { source, destination } = result

    if (!destination) return

    if (destination.droppableId === source.droppableId && destination.index === source.index) {
      return
    }

    const newTasks = Array.from(tasks)
    const sourceList = newTasks.filter((task) => task.status === source.droppableId)
    const destList = newTasks.filter((task) => task.status === destination.droppableId)

    const [movedTask] = sourceList.splice(source.index, 1)

    movedTask.status = destination.droppableId as Task["status"]

    // Update isCompleted based on the new status
    if (destination.droppableId === "done") {
      movedTask.isCompleted = true
    } else if (source.droppableId === "done") {
      movedTask.isCompleted = false
    }

    destList.splice(destination.index, 0, movedTask)

    const updatedTasks = newTasks
      .filter((task) => task.status !== source.droppableId && task.status !== destination.droppableId)
      .concat(sourceList)
      .concat(destList)

    setTasks(updatedTasks)

    toast({
      title: "Task Moved",
      description: `Task "${movedTask.title}" moved to ${destination.droppableId}.`,
    })
  }

  const addTask = () => {
    if (newTask.title && newTask.description) {
      setTasks([...tasks, { ...newTask, id: Date.now().toString(), status: "todo", isCompleted: false } as Task])
      setNewTask({
        title: "",
        description: "",
        priority: "medium",
        category: "",
        dueDate: "",
        assignee: "",
        isCompleted: false,
      })
      toast({
        title: "Task Added",
        description: "New task has been successfully added.",
      })
    }
  }

  const openEditModal = (task: Task) => {
    setEditingTask(task)
    setIsEditModalOpen(true)
  }

  const updateTask = () => {
    if (editingTask) {
      setTasks(tasks.map((task) => (task.id === editingTask.id ? editingTask : task)))
      setIsEditModalOpen(false)
      setEditingTask(null)
      toast({
        title: "Task Updated",
        description: "Task has been successfully updated.",
      })
    }
  }

  const toggleTaskCompletion = (taskId: string) => {
    setTasks(
      tasks.map((task) =>
        task.id === taskId
          ? { ...task, isCompleted: !task.isCompleted, status: !task.isCompleted ? "done" : task.status }
          : task,
      ),
    )
    toast({
      title: "Task Status Changed",
      description: "Task completion status has been updated.",
    })
  }

  const deleteTask = (taskId: string) => {
    setTasks(tasks.filter((task) => task.id !== taskId))
    toast({
      title: "Task Deleted",
      description: "The task has been successfully deleted.",
      variant: "destructive",
    })
  }

  return (
    <div className="flex h-full bg-gray-100 dark:bg-gray-900">
      <div className="w-full p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-200">Environmental Tasks</h2>
          <Dialog open={isAddTaskModalOpen} onOpenChange={setIsAddTaskModalOpen}>
            <DialogTrigger asChild>
              <Button className="bg-green-500 hover:bg-green-600 text-white">
                <Plus className="mr-2 h-4 w-4" /> Add New Task
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Add New Task</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="new-title">Title</Label>
                  <Input
                    id="new-title"
                    value={newTask.title}
                    onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new-description">Description</Label>
                  <Textarea
                    id="new-description"
                    value={newTask.description}
                    onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new-priority">Priority</Label>
                  <Select
                    value={newTask.priority}
                    onValueChange={(value) => setNewTask({ ...newTask, priority: value as "low" | "medium" | "high" })}
                  >
                    <SelectTrigger id="new-priority">
                      <SelectValue placeholder="Select Priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new-category">Category</Label>
                  <Input
                    id="new-category"
                    value={newTask.category}
                    onChange={(e) => setNewTask({ ...newTask, category: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new-dueDate">Due Date</Label>
                  <Input
                    id="new-dueDate"
                    type="date"
                    value={newTask.dueDate}
                    onChange={(e) => setNewTask({ ...newTask, dueDate: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new-assignee">Assignee</Label>
                  <Input
                    id="new-assignee"
                    value={newTask.assignee}
                    onChange={(e) => setNewTask({ ...newTask, assignee: e.target.value })}
                  />
                </div>
                <Button
                  onClick={() => {
                    addTask()
                    setIsAddTaskModalOpen(false)
                  }}
                  className="w-full"
                >
                  Add Task
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
        <DragDropContext onDragEnd={onDragEnd}>
          <div className="grid grid-cols-3 gap-6 h-[calc(100vh-150px)]">
            {["todo", "inProgress", "done"].map((status) => (
              <Droppable key={status} droppableId={status}>
                {(provided, snapshot) => (
                  <div
                    {...provided.droppableProps}
                    ref={provided.innerRef}
                    className={`p-4 rounded-lg bg-white dark:bg-gray-800 shadow-md ${
                      snapshot.isDraggingOver ? "ring-2 ring-blue-400" : ""
                    }`}
                  >
                    <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200 capitalize">
                      {status.replace(/([A-Z])/g, " $1").trim()}
                    </h3>
                    <ScrollArea className="h-[calc(100vh-250px)]">
                      {tasks
                        .filter((task) => task.status === status)
                        .map((task, index) => (
                          <Draggable key={task.id} draggableId={task.id} index={index}>
                            {(provided, snapshot) => (
                              <Card
                                ref={provided.innerRef}
                                {...provided.draggableProps}
                                {...provided.dragHandleProps}
                                className={`mb-3 ${
                                  snapshot.isDragging
                                    ? "shadow-lg ring-2 ring-blue-400"
                                    : "hover:shadow-md transition-shadow duration-200"
                                }`}
                              >
                                <CardHeader className="p-4">
                                  <CardTitle className="flex justify-between items-center text-lg font-semibold">
                                    <span className={task.isCompleted ? "line-through text-gray-500" : ""}>
                                      {task.title}
                                    </span>
                                    <div className="flex items-center space-x-2">
                                      <Checkbox
                                        checked={task.isCompleted}
                                        onCheckedChange={() => toggleTaskCompletion(task.id)}
                                      />
                                      <Button variant="ghost" size="sm" onClick={() => openEditModal(task)}>
                                        <Edit className="h-4 w-4" />
                                      </Button>
                                      <Button variant="ghost" size="sm" onClick={() => deleteTask(task.id)}>
                                        <Trash2 className="h-4 w-4 text-red-500" />
                                      </Button>
                                    </div>
                                  </CardTitle>
                                </CardHeader>
                                <CardContent className="p-4 pt-0">
                                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{task.description}</p>
                                  <div className="flex flex-wrap items-center gap-2">
                                    <span
                                      className={`px-2 py-1 text-xs font-semibold rounded-full ${
                                        task.priority === "high"
                                          ? "bg-red-100 text-red-800"
                                          : task.priority === "medium"
                                            ? "bg-yellow-100 text-yellow-800"
                                            : "bg-green-100 text-green-800"
                                      }`}
                                    >
                                      {task.priority}
                                    </span>
                                    <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
                                      <Calendar className="inline-block w-3 h-3 mr-1" />
                                      {task.dueDate}
                                    </span>
                                    <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
                                      <Users className="inline-block w-3 h-3 mr-1" />
                                      {task.assignee}
                                    </span>
                                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                                      {task.category}
                                    </span>
                                  </div>
                                </CardContent>
                              </Card>
                            )}
                          </Draggable>
                        ))}
                      {provided.placeholder}
                    </ScrollArea>
                  </div>
                )}
              </Droppable>
            ))}
          </div>
        </DragDropContext>
      </div>

      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Edit Task</DialogTitle>
          </DialogHeader>
          {editingTask && (
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="edit-title">Title</Label>
                <Input
                  id="edit-title"
                  value={editingTask.title}
                  onChange={(e) => setEditingTask({ ...editingTask, title: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-description">Description</Label>
                <Textarea
                  id="edit-description"
                  value={editingTask.description}
                  onChange={(e) => setEditingTask({ ...editingTask, description: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-priority">Priority</Label>
                <Select
                  value={editingTask.priority}
                  onValueChange={(value) =>
                    setEditingTask({ ...editingTask, priority: value as "low" | "medium" | "high" })
                  }
                >
                  <SelectTrigger id="edit-priority">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-category">Category</Label>
                <Input
                  id="edit-category"
                  value={editingTask.category}
                  onChange={(e) => setEditingTask({ ...editingTask, category: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-dueDate">Due Date</Label>
                <Input
                  id="edit-dueDate"
                  type="date"
                  value={editingTask.dueDate}
                  onChange={(e) => setEditingTask({ ...editingTask, dueDate: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-assignee">Assignee</Label>
                <Input
                  id="edit-assignee"
                  value={editingTask.assignee}
                  onChange={(e) => setEditingTask({ ...editingTask, assignee: e.target.value })}
                />
              </div>
              <Button onClick={updateTask} className="w-full">
                Update Task
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

