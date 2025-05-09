"use client";
import { useEffect, useState } from "react";

import { API_BASE_URL } from "@/constants/URL";
import { Bot, CirclePlus, Loader2, Search } from "lucide-react";
import { useSession } from "next-auth/react";

import { Role } from "@/constants/Role";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import axiosInstance from "@/lib/Api-Instance";
import Image from "next/image";
import { Switch } from "../ui/switch";
import { cn } from "@/lib/utils";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { Loading } from "../loading";
import { useModal } from "@/hooks/use-modal-store";
import Link from "next/link";
import ModelCard from "@/components/assistant-ai/ModelCard";

export interface Models {
    id: string;
    title: string;
    description: string;
    author: string;
    is_active: boolean;
    image_url: string;
    isEditable: boolean;
    groupId?: string;
}

const Models = ({ groupId }: { groupId?: string }) => {
    const { data: session, status } = useSession();
    // const { t: trans } = useTranslation();
    const router = useRouter();
    // const { setIsLoading } = useLoading();
    const { onOpen, isOpen, isSubmit } = useModal();

    const [searchTerm, setSearchTerm] = useState<string>("");
    const [models, setModels] = useState<Models[]>([]);
    const [isPopupOpen, setIsPopupOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [isEnabled, setIsEnabled] = useState(false);

    const handleToggle = async (id: string) => {
        const url = `${API_BASE_URL}/models/toggle/is-active/${id}`;
        console.log(url);
        setIsLoading(true);
        try {
            const response = await axiosInstance.put(url);
            if (response.status === 200) {
                const data = response.data.data;
                setIsEnabled(data.is_active);
            }
            setIsLoading(false);
        } catch (error) {
            console.error("Lỗi khi lấy môn học:", error);
            setIsLoading(false);
        }
    };

    // const handleAddNew = () => {
    //     router.push({
    //         pathname: "/admin/models/detail",
    //         query: { groupId: groupId || "" }
    //     });
    // };

    const handleOpenPopup = () => {
        if (!groupId) {
            toast.error("Vui lòng chọn một nhóm trước khi gán mô hình.");
            return;
        }
        setIsPopupOpen(true);
    };

    const handleModelAssigned = () => {
        getModels();
    };

    const filteredModels = models.filter((model) => {
        const combinedString =
            (model.title || "") + (model.description || "") + (model.author || "");
        return combinedString.toLowerCase().includes(searchTerm.toLowerCase());
    });

    const getModels = async () => {
        const url = groupId
            ? `${API_BASE_URL}/groups/${groupId}/models`
            : `${API_BASE_URL}/models`;

        setIsLoading(true);
        try {
            const response = await axiosInstance.get(url);
            // console.log("Response:", response.data.data);

            if (response.status === 200) {
                // console.log("Models:", response.data.data);
                setModels(response.data.data);
            }
            setIsLoading(false);
        } catch (error) {
            console.error("Error fetching models:", error);
            setIsLoading(false);
        }
    }

    useEffect(() => {
        getModels();
    }, [groupId, isSubmit]);

    const isAdmin = session?.user?.role === Role.ADMIN;
    const isTeacher = session?.user?.role === Role.TEACHER;
    const canEdit = isAdmin || isTeacher;

    const handleModelUpdated = (modelId: string, isActive: boolean) => {
        // Update the models state with the new active status
        setModels(prevModels =>
            prevModels.map(model =>
                model.id === modelId
                    ? { ...model, is_active: isActive }
                    : model
            )
        );
    };

    const handleEditModel = (model: Models) => {
        // Implementation to handle editing a model
        // For example, open a modal or navigate to edit page
        // router.push(`/admin/models/edit/${model.id}`);
        // or
        // onOpen("editAssistant", { model });

        console.log("Edit model:", model);
    };

    // const handleDeleteModel = async (model: Models) => {
    //     // Implementation to handle deleting a model
    //     // You might want to show a confirmation dialog first
    //     // onOpen("deleteAssistant",  model );
       
    //     // if (confirm(`Are you sure you want to delete ${model.title}?`)) {
    //     //     try {
    //     //         await axiosInstance.delete(`${API_BASE_URL}/models/${model.id}`);
    //     //         toast.success("Model deleted successfully");
    //     //         // Refresh the models list
    //     //         getModels();
    //     //     } catch (error) {
    //     //         console.error("Error deleting model:", error);
    //     //         toast.error("Failed to delete model");
    //     //     }
    //     // }
    // };

    return (
        <div className="w-full h-full space-y-6">
            <div className="bg-white mb-2 dark:bg-gray-800 shadow-md rounded-lg p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="relative w-full md:w-1/3">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Search className="h-4 w-4 text-gray-400 dark:text-gray-400" />
                    </div>
                    <Input
                        type="text"
                        placeholder="Tìm kiếm mô hình..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-700 focus-visible:ring-sky-500 focus-visible:ring-offset-0"
                    />
                </div>

                {canEdit && (
                    <div className="flex items-center gap-3 self-end">
                        <Button
                            onClick={handleOpenPopup}
                            hidden={!groupId}
                            variant="outline"
                            className="bg-amber-50 hover:bg-amber-100 text-amber-700 border-amber-200 hover:border-amber-300 dark:bg-amber-900/20 dark:text-amber-300 dark:border-amber-700 dark:hover:bg-amber-900/30"
                        >
                            <Bot className="w-4 h-4 mr-2" />
                            Gán mô hình
                        </Button>
                        <Button
                            onClick={() => onOpen("createAssistant")}
                            className="bg-sky-400 hover:bg-sky-500 text-white"
                        >
                            <CirclePlus className="w-4 h-4 mr-2" />
                            Thêm mới
                        </Button>
                    </div>
                )}
            </div>

            <div className="bg-gray-200 dark:bg-gray-800 rounded-lg shadow-md p-4 overflow-hidden flex flex-col h-[calc(100vh-160px)]">
                {isLoading ? (
                    <Loading />
                ) : filteredModels.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 overflow-y-auto">
                        {filteredModels.map((model, index) => (
                            <ModelCard
                                key={model.id || index}
                                model={model}
                                canEdit={canEdit}
                                onModelUpdated={handleModelUpdated}
                                onEdit={handleEditModel}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center h-full">
                        <div className="bg-gray-100 dark:bg-gray-700 rounded-full p-6">
                            <Bot className="w-12 h-12 text-gray-400 dark:text-gray-500" />
                        </div>
                        <p className="mt-4 text-gray-500 dark:text-gray-400">Không có mô hình nào.</p>
                        {canEdit && (
                            <Button
                                onClick={() => router.push("/admin/models/detail")}
                                variant="outline"
                                size="sm"
                                className="mt-4 text-sky-400 dark:text-sky-400"
                            >
                                <CirclePlus className="w-4 h-4 mr-2" />
                                Tạo mô hình mới
                            </Button>
                        )}
                    </div>
                )}
            </div>
            {/* {groupId && (
                <ModelAssignmentPopup
                    isOpen={isPopupOpen}
                    onClose={() => setIsPopupOpen(false)}
                    groupId={groupId}
                    onModelAssigned={handleModelAssigned}
                />
            )} */}
        </div >
    );
};

export default Models;