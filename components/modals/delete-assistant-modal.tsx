"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button";
import { useModal } from "@/hooks/use-modal-store";
import { toast } from "sonner";
import axiosInstance from "@/lib/Api-Instance";
import { API_BASE_URL } from "@/constants/URL";

export const DeleteAssistantModal = () => {
    const { isOpen, onClose, type, data, onSave, cleanupModalEffects } = useModal();
    const router = useRouter();

    const isModalOpen = isOpen && type === "deleteAssistant";
    const model = data;

    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        return () => {
            if (isModalOpen) {
                cleanupModalEffects();
            }
        };
    }, [isModalOpen, cleanupModalEffects]);

    const handleClose = () => {
        if (!isLoading) {
            onClose();
            setTimeout(() => {
                cleanupModalEffects();
            }, 50);
        }
    };

    const handleDelete = async () => {
        if (!model?.id) {
            toast.error("Không thể xóa model này");
            return;
        }

        try {
            setIsLoading(true);

            const response = await axiosInstance.delete(`${API_BASE_URL}/models/${model.id}`);

            if (response.status === 200) {
                toast.success("Xóa model thành công");
                onSave(); // Signal parent component to refresh the model list
            }
        } catch (error) {
            console.error("Lỗi khi xóa model:", error);
            toast.error("Có lỗi xảy ra khi xóa model");
        } finally {
            setIsLoading(false);
            handleClose();
        }
    };

    // Thêm một kiểm soát chặt chẽ hơn về trạng thái dialog
    const onOpenChange = (open: boolean) => {
        if (!open && !isLoading) {
            handleClose();
        }
    };

    return (
        <Dialog open={isModalOpen} onOpenChange={onOpenChange}>
            <DialogContent className="bg-white dark:bg-gray-800 text-black dark:text-white p-0 overflow-hidden" onEscapeKeyDown={handleClose} onPointerDownOutside={handleClose}>
                <DialogHeader className="pt-8 px-6">
                    <DialogTitle className="text-2xl text-center font-bold">
                        Xóa trợ lý Ai
                    </DialogTitle>
                    <DialogDescription className="text-center text-zinc-500 dark:text-zinc-400">
                        Trợ lý Ai <span className="text-indigo-500 font-semibold">{model?.title}</span> sẽ bị xóa.
                    </DialogDescription>
                </DialogHeader>
                <DialogFooter className="bg-gray-100 dark:bg-gray-700 px-6 py-4">
                    <div className="flex items-center justify-between w-full">
                        <Button
                            disabled={isLoading}
                            onClick={handleClose}
                            variant="ghost"
                        >
                            Hủy
                        </Button>
                        <Button
                            disabled={isLoading}
                            onClick={handleDelete}
                            variant="destructive"
                        >
                            {isLoading ? "Đang xóa..." : "Xác nhận"}
                        </Button>
                    </div>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
};