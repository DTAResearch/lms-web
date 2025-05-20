"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle
} from "@/components/ui/dialog"
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { useModal } from "@/hooks/use-modal-store";
import { toast } from "sonner";
import axiosInstance from "@/lib/Api-Instance";
import { API_BASE_URL } from "@/constants/URL";
import { on } from "events";
import { Input } from "../ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";

const formSchema = z.object({
    name: z.string().min(1, { message: "Tên không được để trống" }),
    email: z.string().email({ message: "Email không hợp lệ" }),
    role: z.enum(["admin", "teacher", "student", "manager"]),
});

export const CreateUserModal = () => {
    const { isOpen, onClose, type, data, onSave } = useModal();
    const router = useRouter();
    const isModalOpen = isOpen && type === "createUser";
    const user = data;
    const [isLoading, setIsLoading] = useState(false);

    const form = useForm({
        resolver: zodResolver(formSchema),
        defaultValues: {
            name: user?.name || "",
            email: user?.email || "",
            role: user?.role || "student",
        },
    });

    const onSubmit = async (values: z.infer<typeof formSchema>) => {
        try {
            console.log("Submitting form with values:", values);
            toast.success("Tạo người dùng mới thành công");

        } catch (error) {
            console.error("Error creating user:", error);
            toast.error("Đã xảy ra lỗi khi tạo người dùng");

        }
    }

     const handleClose = () => {
        form.reset();
        onClose();
    };


    return (
        <Dialog
            open={isModalOpen}
            onOpenChange={handleClose}
        >
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Tạo người dùng mới</DialogTitle>
                    <DialogDescription>
                        Nhập thông tin người dùng mới để tạo tài khoản.
                    </DialogDescription>
                </DialogHeader>

                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                        <FormField
                            control={form.control}
                            name="name"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Tên</FormLabel>
                                    <FormControl>
                                        <Input
                                            {...field}
                                            className="bg-white dark:bg-gray-700"
                                            placeholder="Nhập tên"
                                            disabled={isLoading}
                                            maxLength={50}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="email"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Email</FormLabel>
                                    <FormControl>
                                        <Input
                                            {...field}
                                            type="email"
                                            placeholder="Nhập email"
                                            className="bg-white dark:bg-gray-700"
                                            disabled={isLoading}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="role"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Vai trò</FormLabel>
                                    <Select
                                        onValueChange={field.onChange}
                                        defaultValue={field.value}
                                        disabled={isLoading}
                                    >   
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Chọn vai trò" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            <SelectItem value="admin">Quản trị viên</SelectItem>
                                            <SelectItem value="teacher">Giáo viên</SelectItem>
                                            <SelectItem value="student">Học sinh</SelectItem>
                                            <SelectItem value="manager">Quản lý</SelectItem>
                                        </SelectContent>
                                    </Select>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <DialogFooter>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleClose}
                                disabled={isLoading}
                            >
                                Hủy
                            </Button>
                            <Button
                                type="submit"
                                variant="primary"
                                disabled={isLoading}
                            >
                                {isLoading ? "Đang tạo..." : "Tạo người dùng"}
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>


            </DialogContent>
        </Dialog>
    );
}