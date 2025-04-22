"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { CheckIcon, Info, X } from "lucide-react";

import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogFooter,
    DialogTitle,
    DialogDescription,
} from "@/components/ui/dialog";

import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

import {
    Command,
    CommandDialog,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from "@/components/ui/command";

import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/constants/URL";
import { useModal } from "@/hooks/use-modal-store";
import { Loader2 } from "lucide-react";
import axiosInstance from "@/lib/Api-Instance";

// Form schema using zod
const formSchema = z.object({
    name: z.string().min(1, { message: "Tên mô hình không được để trống" }),
    modelId: z.string().min(1, { message: "ID mô hình không được để trống" }),
    baseModelId: z.string().min(1, { message: "Vui lòng chọn mô hình cơ sở" }),
    description: z.string().optional(),
    systemPrompt: z.string().optional(),
    imageUrl: z.string().url({ message: "URL ảnh không hợp lệ" }).optional(),
    visibility: z.enum(["PUBLIC", "PRIVATE"], {
        required_error: "Vui lòng chọn phạm vi truy cập",
    }),
    visionEnabled: z.boolean().default(false),
    usageEnabled: z.boolean().default(false),
    citationsEnabled: z.boolean().default(true),
});

export const CreateAssistant = () => {
    const { isOpen, onClose, type, data } = useModal();
    const isModalOpen = isOpen && type === "createAssistant";
    const { modelId: editModelId, groupId } = data || {};
    const isEditing = !!editModelId;

    const [baseModels, setBaseModels] = useState<string[]>([]);
    const [groups, setGroups] = useState<{ id: string; name: string }[]>([]);
    const [knowledgeBases, setKnowledgeBases] = useState<{ id: string; name: string }[]>([]);
    const [selectedGroups, setSelectedGroups] = useState<string[]>([]);
    const [selectedKnowledge, setSelectedKnowledge] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isFetchingData, setIsFetchingData] = useState(false);

    // Form setup
    const form = useForm({
        resolver: zodResolver(formSchema),
        defaultValues: {
            name: "",
            modelId: "",
            baseModelId: "",
            description: "",
            systemPrompt: "",
            imageUrl: "",
            visibility: "PUBLIC",
            visionEnabled: false,
            usageEnabled: false,
            citationsEnabled: true,
        }
    });

    // Generate model ID from name
    const createIdFromName = (name: string) => {
        if (!name) return "";

        let id = name
            .toLowerCase()
            .trim()
            .replace(/\s+/g, "-")
            .replace(/[^\w\s-]/g, "")
            .replace(/-+/g, "-");

        // Remove Vietnamese accents
        id = id.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        id = id.replace(/[đĐ]/g, "d");

        return id;
    };

    // Watch name field to auto-generate ID
    const watchName = form.watch("name");
    useEffect(() => {
        if (!isEditing && watchName) {
            form.setValue("modelId", createIdFromName(watchName));
        }
    }, [watchName, form, isEditing]);

    // Fetch base models
    const fetchBaseModels = async () => {
        try {
            setIsFetchingData(true);
            const response = await axiosInstance.get(`${API_BASE_URL}/models/base`);
            if (response.status === 200) {
                setBaseModels(response.data.data);
                if (response.data.data.length > 0 && !editModelId) {
                    form.setValue("baseModelId", response.data.data[0]);
                }
            }
        } catch (error) {
            console.error("Error fetching base models:", error);
            toast.error("Không thể tải danh sách mô hình cơ sở");
        } finally {
            setIsFetchingData(false);
        }
    };

    // Fetch groups
    const fetchGroups = async () => {
        try {
            setIsFetchingData(true);
            const response = await axiosInstance.get(`${API_BASE_URL}/groups`);
            if (response.status === 200) {
                setGroups(response.data.data);
            }
        } catch (error) {
            console.error("Error fetching groups:", error);
            toast.error("Không thể tải danh sách nhóm");
        } finally {
            setIsFetchingData(false);
        }
    };

    // Fetch knowledge bases
    const fetchKnowledgeBases = async () => {
        try {
            setIsFetchingData(true);
            const response = await axiosInstance.get(`${API_BASE_URL}/knowledge`);
            if (response.status === 200) {
                setKnowledgeBases(response.data.data);
            }
        } catch (error) {
            console.error("Error fetching knowledge bases:", error);
            toast.error("Không thể tải danh sách kho kiến thức");
        } finally {
            setIsFetchingData(false);
        }
    };

    // Fetch model details for editing
    const fetchModelDetails = async () => {
        if (!editModelId) return;

        try {
            setIsFetchingData(true);
            const response = await axiosInstance.get(`${API_BASE_URL}/models/${editModelId}`);
            if (response.status === 200) {
                const modelData = response.data.data;

                form.setValue("name", modelData.name);
                form.setValue("modelId", modelData.model_id);
                form.setValue("baseModelId", modelData.base_model_id);
                form.setValue("description", modelData.description || "");
                form.setValue("systemPrompt", modelData.system_prompt || "");
                form.setValue("imageUrl", modelData.profile_image_url || "");
                form.setValue("visibility", modelData.access_control ? "PRIVATE" : "PUBLIC");

                if (modelData.capabilities) {
                    form.setValue("visionEnabled", modelData.capabilities.vision || false);
                    form.setValue("usageEnabled", modelData.capabilities.usage || false);
                    form.setValue("citationsEnabled", modelData.capabilities.citations || false);
                }

                if (modelData.access_control?.read?.group_ids) {
                    setSelectedGroups(modelData.access_control.read.group_ids);
                }

                if (modelData.knowledge) {
                    setSelectedKnowledge(modelData.knowledge.map((item: any) => item.id));
                }
            }
        } catch (error) {
            console.error("Error fetching model details:", error);
            toast.error("Không thể tải thông tin mô hình");
        } finally {
            setIsFetchingData(false);
        }
    };

    // Initial data loading
    useEffect(() => {
        if (isModalOpen) {
            fetchBaseModels();
            fetchGroups();
            fetchKnowledgeBases();
            if (editModelId) {
                fetchModelDetails();
            }
        }
    }, [isModalOpen, editModelId]);

    // Form submission
    const onSubmit = async (values: z.infer<typeof formSchema>) => {
        try {
            setIsLoading(true);

            // Structure access control according to API requirements
            let accessControl = null;
            if (values.visibility === "PRIVATE") {
                accessControl = {
                    read: {
                        group_ids: selectedGroups,
                        user_ids: [] // Required empty array
                    },
                    write: {
                        group_ids: [], // Required empty array
                        user_ids: []  // Required empty array
                    }
                };
            }

            // Format capabilities object
            const capabilities = {
                vision: values.visionEnabled,
                usage: values.usageEnabled,
                citations: values.citationsEnabled,
            };

            // Format knowledge base items correctly
            const knowledgeItems = selectedKnowledge.map(kbId => {
                const kb = knowledgeBases.find(k => k.id === kbId);
                return {
                    id: kbId,
                    name: kb?.name || "",
                    // Add any additional required properties
                };
            });

            // Structure the request according to API requirements
            const requestData = {
                id: values.modelId,
                name: values.name,
                base_model_id: values.baseModelId,
                params: {
                    system: values.systemPrompt || "" // Use system as the property name
                },
                access_control: accessControl,
                meta: {
                    capabilities: capabilities,
                    description: values.description || "",
                    profile_image_url: values.imageUrl || "",
                    suggestion_prompts: [], // Required empty array
                    tags: [], // Required empty array
                    knowledge: knowledgeItems // Correctly formatted knowledge items
                }
            };

            console.log("Sending request data:", requestData);

            if (isEditing) {
                // Update existing model
                const response = await axiosInstance.put(`${API_BASE_URL}/models/${editModelId}`, requestData);
                if (response.status === 200) {
                    toast.success("Cập nhật mô hình thành công");
                    handleClose();
                }
            } else {
                // Create new model
                const response = await axiosInstance.post(`${API_BASE_URL}/models`, requestData);
                if (response.status === 200) {
                    toast.success("Tạo mô hình thành công");
                    handleClose();
                }
            }
        } catch (error: any) {
            console.error("Error submitting form:", error);
            toast.error(error.response?.data?.message || "Có lỗi xảy ra khi lưu mô hình");
        } finally {
            setIsLoading(false);
        }
    };

    const handleClose = () => {
        form.reset();
        setSelectedGroups([]);
        setSelectedKnowledge([]);
        onClose();
    };

    if (!isModalOpen) return null;

    return (
        <Dialog open={isModalOpen} onOpenChange={handleClose}>
            <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto bg-white dark:bg-gray-800">
                <DialogHeader>
                    <DialogTitle className="text-xl font-bold text-center">
                        {isEditing ? "Chỉnh sửa mô hình AI" : "Tạo mô hình AI mới"}
                    </DialogTitle>
                    <DialogDescription className="text-center text-gray-500 dark:text-gray-400">
                        {isEditing ? "Cập nhật thông tin cho mô hình AI hiện có" : "Tạo và tùy chỉnh một mô hình AI mới"}
                    </DialogDescription>
                </DialogHeader>

                {isFetchingData ? (
                    <div className="flex items-center justify-center py-10">
                        <Loader2 className="w-8 h-8 text-sky-500 animate-spin" />
                        <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">Đang tải dữ liệu...</span>
                    </div>
                ) : (
                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                            <Tabs defaultValue="basic" className="w-full">
                                <TabsList className="grid grid-cols-3 mb-4">
                                    <TabsTrigger value="basic">Thông tin cơ bản</TabsTrigger>
                                    <TabsTrigger value="permissions">Quyền truy cập</TabsTrigger>
                                    <TabsTrigger value="advanced">Cấu hình nâng cao</TabsTrigger>
                                </TabsList>

                                <TabsContent value="basic" className="space-y-4">
                                    {/* Basic information tab */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <FormField
                                            control={form.control}
                                            name="name"
                                            render={({ field }) => (
                                                <FormItem>
                                                    <FormLabel className="font-medium text-gray-700 dark:text-gray-300">Tên mô hình</FormLabel>
                                                    <FormControl>
                                                        <Input
                                                            {...field}
                                                            placeholder="Nhập tên mô hình"
                                                            className="bg-white dark:bg-gray-700"
                                                            disabled={isLoading}
                                                        />
                                                    </FormControl>
                                                    <FormDescription className="text-xs text-gray-500 dark:text-gray-400">
                                                        Đây là tên hiển thị cho mô hình của bạn
                                                    </FormDescription>
                                                    <FormMessage />
                                                </FormItem>
                                            )}
                                        />

                                        <FormField
                                            control={form.control}
                                            name="modelId"
                                            render={({ field }) => (
                                                <FormItem>
                                                    <FormLabel className="font-medium text-gray-700 dark:text-gray-300">ID mô hình</FormLabel>
                                                    <FormControl>
                                                        <Input
                                                            {...field}
                                                            placeholder="model-id"
                                                            className="bg-gray-50 dark:bg-gray-700"
                                                            //   disabled={isEditing || isLoading}
                                                            disabled={true}
                                                        />
                                                    </FormControl>
                                                    <FormDescription className="text-xs text-gray-500 dark:text-gray-400">
                                                        Định danh duy nhất cho mô hình của bạn
                                                    </FormDescription>
                                                    <FormMessage />
                                                </FormItem>
                                            )}
                                        />
                                    </div>

                                    <FormField
                                        control={form.control}
                                        name="baseModelId"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel className="font-medium text-gray-700 dark:text-gray-300">Mô hình cơ sở</FormLabel>
                                                <Select
                                                    onValueChange={field.onChange}
                                                    defaultValue={field.value}
                                                    value={field.value}
                                                    disabled={isLoading}
                                                >
                                                    <FormControl>
                                                        <SelectTrigger className="bg-white dark:bg-gray-700">
                                                            <SelectValue placeholder="Chọn mô hình cơ sở" />
                                                        </SelectTrigger>
                                                    </FormControl>
                                                    <SelectContent>
                                                        {baseModels.map((model) => (
                                                            <SelectItem key={model} value={model}>
                                                                {model}
                                                            </SelectItem>
                                                        ))}
                                                    </SelectContent>
                                                </Select>
                                                <FormDescription className="text-xs text-gray-500 dark:text-gray-400">
                                                    Mô hình AI cơ sở được sử dụng
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />

                                    <FormField
                                        control={form.control}
                                        name="description"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel className="font-medium text-gray-700 dark:text-gray-300">Mô tả</FormLabel>
                                                <FormControl>
                                                    <Textarea
                                                        {...field}
                                                        placeholder="Nhập mô tả về mô hình của bạn"
                                                        className="min-h-[80px] bg-white dark:bg-gray-700 resize-none"
                                                        disabled={isLoading}
                                                    />
                                                </FormControl>
                                                <FormDescription className="text-xs text-gray-500 dark:text-gray-400">
                                                    Mô tả ngắn gọn về mục đích và khả năng của mô hình
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />

                                    <FormField
                                        control={form.control}
                                        name="imageUrl"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel className="font-medium text-gray-700 dark:text-gray-300">URL hình ảnh</FormLabel>
                                                <FormControl>
                                                    <Input
                                                        {...field}
                                                        placeholder="https://example.com/image.png"
                                                        className="bg-white dark:bg-gray-700"
                                                        disabled={isLoading}
                                                    />
                                                </FormControl>
                                                <FormDescription className="text-xs text-gray-500 dark:text-gray-400">
                                                    URL hình ảnh đại diện cho mô hình của bạn
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />
                                </TabsContent>

                                <TabsContent value="permissions" className="space-y-4">
                                    {/* Permissions tab */}
                                    <FormField
                                        control={form.control}
                                        name="visibility"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel className="font-medium text-gray-700 dark:text-gray-300">Phạm vi truy cập</FormLabel>
                                                <Select
                                                    onValueChange={field.onChange}
                                                    defaultValue={field.value}
                                                    value={field.value}
                                                    disabled={isLoading}
                                                >
                                                    <FormControl>
                                                        <SelectTrigger className="bg-white dark:bg-gray-700">
                                                            <SelectValue placeholder="Chọn phạm vi truy cập" />
                                                        </SelectTrigger>
                                                    </FormControl>
                                                    <SelectContent>
                                                        <SelectItem value="PUBLIC">Công khai</SelectItem>
                                                        <SelectItem value="PRIVATE">Giới hạn</SelectItem>
                                                    </SelectContent>
                                                </Select>
                                                <FormDescription className="text-xs text-gray-500 dark:text-gray-400">
                                                    Xác định ai có thể truy cập mô hình này
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />

                                    {form.watch("visibility") === "PRIVATE" && (
                                        <div className="space-y-4 border rounded-lg p-4 dark:border-gray-700">
                                            <div>
                                                <div className="flex justify-between items-center mb-2">
                                                    <h4 className="font-medium text-sm text-gray-700 dark:text-gray-300">
                                                        Nhóm người dùng có quyền truy cập
                                                    </h4>
                                                    <Badge variant="outline" className="text-xs">
                                                        {selectedGroups.length} đã chọn
                                                    </Badge>
                                                </div>

                                                <div className="relative">
                                                    <Popover modal={true}>
                                                        <PopoverTrigger asChild>
                                                            <Button
                                                                variant="outline"
                                                                className="w-full justify-between bg-white dark:bg-gray-700 text-left font-normal"
                                                                disabled={isLoading}
                                                            >
                                                                <div className="flex items-center">
                                                                    <span>
                                                                        {selectedGroups.length > 0
                                                                            ? `${selectedGroups.length} nhóm đã chọn`
                                                                            : "Chọn nhóm người dùng"}
                                                                    </span>
                                                                    {selectedGroups.length > 0 && (
                                                                        <Badge className="ml-2 bg-sky-500 text-white dark:bg-sky-600 hover:bg-sky-600 dark:hover:bg-sky-700">
                                                                            {selectedGroups.length}
                                                                        </Badge>
                                                                    )}
                                                                </div>
                                                                <Info className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                                                            </Button>
                                                        </PopoverTrigger>
                                                        <PopoverContent
                                                            className="w-full p-0"
                                                            align="start"
                                                            side="bottom"
                                                            sideOffset={4}
                                                            forceMount
                                                            style={{ zIndex: 9999, position: "relative" }}
                                                        >
                                                            {/* <div className="p-2 border-b dark:border-gray-600">
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                  Chọn một hoặc nhiều nhóm người dùng
                                </p>
                              </div> */}
                                                            <Command>
                                                                {/* <CommandInput placeholder="Tìm nhóm..." className="h-9" /> */}
                                                                <CommandList className="max-h-[300px] overflow-auto">
                                                                    <CommandEmpty>Không tìm thấy nhóm nào</CommandEmpty>
                                                                    <CommandGroup heading="Nhóm người dùng">
                                                                        {groups.map((group) => {
                                                                            const isSelected = selectedGroups.includes(group.id);
                                                                            return (
                                                                                <CommandItem
                                                                                    key={group.id}
                                                                                    onSelect={() => {
                                                                                        if (isSelected) {
                                                                                            setSelectedGroups(selectedGroups.filter(id => id !== group.id));
                                                                                        } else {
                                                                                            setSelectedGroups([...selectedGroups, group.id]);
                                                                                        }
                                                                                    }}
                                                                                    className="flex items-center justify-between py-2"
                                                                                >
                                                                                    <div className="flex items-center">
                                                                                        <div className={cn(
                                                                                            "mr-2 flex h-4 w-4 items-center justify-center rounded-sm border border-primary",
                                                                                            isSelected ? "bg-primary text-primary-foreground" : "opacity-50"
                                                                                        )}>
                                                                                            {isSelected && <CheckIcon className="h-3 w-3" />}
                                                                                        </div>
                                                                                        <span>{group.name}</span>
                                                                                    </div>
                                                                                    {isSelected && (
                                                                                        <Badge variant="secondary" className="ml-auto">
                                                                                            Đã chọn
                                                                                        </Badge>
                                                                                    )}
                                                                                </CommandItem>
                                                                            );
                                                                        })}
                                                                    </CommandGroup>
                                                                </CommandList>
                                                                <div className="p-2 border-t flex justify-between items-center dark:border-gray-600">
                                                                    <span className="text-sm text-gray-500 dark:text-gray-400">
                                                                        {selectedGroups.length} nhóm đã chọn
                                                                    </span>
                                                                    <Button
                                                                        variant="ghost"
                                                                        size="sm"
                                                                        onClick={() => setSelectedGroups([])}
                                                                        disabled={selectedGroups.length === 0}
                                                                        className="text-xs"
                                                                    >
                                                                        Bỏ chọn tất cả
                                                                    </Button>
                                                                </div>
                                                            </Command>
                                                        </PopoverContent>
                                                    </Popover>
                                                </div>

                                                {selectedGroups.length > 0 && (
                                                    <div className="flex flex-wrap gap-2 mt-3 max-h-[120px] overflow-y-auto p-2 border rounded-md dark:border-gray-600">
                                                        {selectedGroups.map(groupId => {
                                                            const group = groups.find(g => g.id === groupId);
                                                            return group ? (
                                                                <Badge
                                                                    key={groupId}
                                                                    variant="secondary"
                                                                    className="px-2 py-1 text-xs flex items-center gap-1 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600"
                                                                >
                                                                    {group.name}
                                                                    <button
                                                                        type="button"
                                                                        className="ml-1 rounded-full hover:bg-gray-300 dark:hover:bg-gray-500 p-0.5 focus:outline-none"
                                                                        onClick={(e) => {
                                                                            e.stopPropagation(); // Stop event from bubbling
                                                                            e.preventDefault(); // Prevent default behavior
                                                                            setSelectedGroups(selectedGroups.filter(id => id !== groupId));
                                                                        }}
                                                                    >
                                                                        <X className="h-3 w-3" />
                                                                    </button>
                                                                </Badge>
                                                            ) : null;
                                                        })}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </TabsContent>

                                <TabsContent value="advanced" className="space-y-4">
                                    {/* Advanced tab */}
                                    <FormField
                                        control={form.control}
                                        name="systemPrompt"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel className="font-medium text-gray-700 dark:text-gray-300">System Prompt</FormLabel>
                                                <FormControl>
                                                    <Textarea
                                                        {...field}
                                                        placeholder="Nhập system prompt cho mô hình AI của bạn"
                                                        className="min-h-[150px] bg-white dark:bg-gray-700"
                                                        disabled={isLoading}
                                                    />
                                                </FormControl>
                                                <FormDescription className="text-xs text-gray-500 dark:text-gray-400">
                                                    Hướng dẫn hệ thống cho mô hình AI của bạn
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />

                                    <div className="space-y-4 border rounded-lg p-4 dark:border-gray-700">
                                        <div className="flex justify-between items-center">
                                            <h4 className="font-medium text-gray-700 dark:text-gray-300">Kho kiến thức liên kết</h4>
                                            <Badge variant="outline" className="text-xs">
                                                {selectedKnowledge.length} đã chọn
                                            </Badge>
                                        </div>

                                        <div className="relative">
                                            <Popover modal={true}>
                                                <PopoverTrigger asChild>
                                                    <Button
                                                        variant="outline"
                                                        className="w-full justify-between bg-white dark:bg-gray-700 text-left font-normal"
                                                        disabled={isLoading}
                                                    >
                                                        <div className="flex items-center">
                                                            <span>
                                                                {selectedKnowledge.length > 0
                                                                    ? `${selectedKnowledge.length} kho kiến thức đã chọn`
                                                                    : "Chọn kho kiến thức"}
                                                            </span>
                                                            {selectedKnowledge.length > 0 && (
                                                                <Badge className="ml-2 bg-sky-500 text-white dark:bg-emerald-600 hover:bg-emerald-600 dark:hover:bg-emerald-700">
                                                                    {selectedKnowledge.length}
                                                                </Badge>
                                                            )}
                                                        </div>
                                                        <Info className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                                                    </Button>
                                                </PopoverTrigger>
                                                <PopoverContent
                                                    className="w-full p-0"
                                                    align="start"
                                                    side="bottom"
                                                    sideOffset={4}
                                                    forceMount

                                                >
                                                    <div className="p-2 border-b dark:border-gray-600">
                                                        <p className="text-sm text-gray-500 dark:text-gray-400">
                                                            Chọn một hoặc nhiều kho kiến thức để liên kết với mô hình
                                                        </p>
                                                    </div>
                                                    <Command className="w-full">
                                                        <CommandInput placeholder="Tìm kho kiến thức..." className="h-9" />
                                                        <CommandList className="max-h-[300px] overflow-auto">
                                                            <CommandEmpty>Không tìm thấy kho kiến thức nào</CommandEmpty>
                                                            <CommandGroup heading="Kho kiến thức">
                                                                {knowledgeBases.map((kb) => {
                                                                    const isSelected = selectedKnowledge.includes(kb.id);
                                                                    return (
                                                                        <CommandItem
                                                                            key={kb.id}
                                                                            onSelect={() => {
                                                                                if (isSelected) {
                                                                                    setSelectedKnowledge(selectedKnowledge.filter(id => id !== kb.id));
                                                                                } else {
                                                                                    setSelectedKnowledge([...selectedKnowledge, kb.id]);
                                                                                }
                                                                            }}
                                                                            className="flex items-center justify-between py-2"
                                                                        >
                                                                            <div className="flex items-center">
                                                                                <div className={cn(
                                                                                    "mr-2 flex h-4 w-4 items-center justify-center rounded-sm border border-primary",
                                                                                    isSelected ? "bg-primary text-primary-foreground" : "opacity-50"
                                                                                )}>
                                                                                    {isSelected && <CheckIcon className="h-3 w-3" />}
                                                                                </div>
                                                                                <span>{kb.name}</span>
                                                                            </div>
                                                                            {isSelected && (
                                                                                <Badge variant="secondary" className="ml-auto">
                                                                                    Đã chọn
                                                                                </Badge>
                                                                            )}
                                                                        </CommandItem>
                                                                    );
                                                                })}
                                                            </CommandGroup>
                                                        </CommandList>
                                                        <div className="p-2 border-t flex justify-between items-center dark:border-gray-600">
                                                            <span className="text-sm text-gray-500 dark:text-gray-400">
                                                                {selectedKnowledge.length} kho kiến thức đã chọn
                                                            </span>
                                                            <Button
                                                                variant="ghost"
                                                                size="sm"
                                                                onClick={() => setSelectedKnowledge([])}
                                                                disabled={selectedKnowledge.length === 0}
                                                                className="text-xs"
                                                            >
                                                                Bỏ chọn tất cả
                                                            </Button>
                                                        </div>
                                                    </Command>
                                                </PopoverContent>
                                            </Popover>
                                        </div>

                                        {selectedKnowledge.length > 0 && (
                                            <div className="flex flex-wrap gap-2 mt-3 max-h-[120px] overflow-y-auto p-2 border rounded-md dark:border-gray-600">
                                                {selectedKnowledge.map(kbId => {
                                                    const kb = knowledgeBases.find(k => k.id === kbId);
                                                    return kb ? (
                                                        <Badge
                                                            key={kbId}
                                                            variant="secondary"
                                                            className="px-2 py-1 text-xs flex items-center gap-1 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600"
                                                        >
                                                            {kb.name}
                                                            <button
                                                                type="button"
                                                                className="ml-1 rounded-full hover:bg-gray-300 dark:hover:bg-gray-500 p-0.5 focus:outline-none"
                                                                onClick={(e) => {
                                                                    e.stopPropagation(); // Stop event from bubbling
                                                                    e.preventDefault(); // Prevent default behavior
                                                                    setSelectedKnowledge(selectedKnowledge.filter(id => id !== kbId));
                                                                }}
                                                            >
                                                                <X className="h-3 w-3" />
                                                            </button>
                                                        </Badge>
                                                    ) : null;
                                                })}
                                            </div>
                                        )}
                                    </div>

                                    <div className="space-y-4 border rounded-lg p-4 dark:border-gray-700">
                                        <h4 className="font-medium text-gray-700 dark:text-gray-300">Cấu hình khả năng</h4>

                                        <div className="space-y-4">
                                            <FormField
                                                control={form.control}
                                                name="visionEnabled"
                                                render={({ field }) => (
                                                    <FormItem className="flex flex-row items-center justify-between p-3 border rounded-md bg-white dark:bg-gray-700 dark:border-gray-600">
                                                        <div className="space-y-0.5">
                                                            <FormLabel className="font-medium text-gray-700 dark:text-gray-300">Hỗ trợ vision</FormLabel>
                                                            <FormDescription className="text-xs text-gray-500 dark:text-gray-400">
                                                                Cho phép mô hình xử lý hình ảnh
                                                            </FormDescription>
                                                        </div>
                                                        <FormControl>
                                                            <Switch
                                                                checked={field.value}
                                                                onCheckedChange={field.onChange}
                                                                disabled={isLoading}
                                                            />
                                                        </FormControl>
                                                    </FormItem>
                                                )}
                                            />

                                            <FormField
                                                control={form.control}
                                                name="usageEnabled"
                                                render={({ field }) => (
                                                    <FormItem className="flex flex-row items-center justify-between p-3 border rounded-md bg-white dark:bg-gray-700 dark:border-gray-600">
                                                        <div className="space-y-0.5">
                                                            <FormLabel className="font-medium text-gray-700 dark:text-gray-300">Theo dõi sử dụng</FormLabel>
                                                            <FormDescription className="text-xs text-gray-500 dark:text-gray-400">
                                                                Theo dõi thống kê sử dụng mô hình
                                                            </FormDescription>
                                                        </div>
                                                        <FormControl>
                                                            <Switch
                                                                checked={field.value}
                                                                onCheckedChange={field.onChange}
                                                                disabled={isLoading}
                                                            />
                                                        </FormControl>
                                                    </FormItem>
                                                )}
                                            />

                                            <FormField
                                                control={form.control}
                                                name="citationsEnabled"
                                                render={({ field }) => (
                                                    <FormItem className="flex flex-row items-center justify-between p-3 border rounded-md bg-white dark:bg-gray-700 dark:border-gray-600">
                                                        <div className="space-y-0.5">
                                                            <FormLabel className="font-medium text-gray-700 dark:text-gray-300">Trích dẫn nguồn</FormLabel>
                                                            <FormDescription className="text-xs text-gray-500 dark:text-gray-400">
                                                                Hiển thị trích dẫn cho thông tin từ kho kiến thức
                                                            </FormDescription>
                                                        </div>
                                                        <FormControl>
                                                            <Switch
                                                                checked={field.value}
                                                                onCheckedChange={field.onChange}
                                                                disabled={isLoading}
                                                            />
                                                        </FormControl>
                                                    </FormItem>
                                                )}
                                            />
                                        </div>
                                    </div>
                                </TabsContent>
                            </Tabs>

                            <DialogFooter>
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={handleClose}
                                    disabled={isLoading}
                                    className="border-gray-300 dark:border-gray-600 dark:hover:bg-gray-700"
                                >
                                    Hủy
                                </Button>
                                <Button
                                    type="submit"
                                    // type="button"   
                                    disabled={isLoading}
                                    className="bg-sky-600 hover:bg-sky-700 text-white"
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            Đang xử lý...
                                        </>
                                    ) : isEditing ? (
                                        "Cập nhật mô hình"
                                    ) : (
                                        "Tạo mô hình"
                                    )}
                                </Button>
                            </DialogFooter>
                        </form>
                    </Form>
                )}
            </DialogContent>
        </Dialog>
    );
};