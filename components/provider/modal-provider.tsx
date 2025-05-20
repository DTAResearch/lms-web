"use client";
import { useEffect, useState } from "react";
import { AssistantModal } from "../modals/assitant-modal";
import { DeleteAssistantModal } from "../modals/delete-assistant-modal";
import { CreateUserModal } from "../modals/create-user-modal";

export const ModalProvider = () => {
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        setIsMounted(true);
    }, []);

    if (!isMounted) {
        return null;
    }
    return (
        <>
            <AssistantModal />
            <DeleteAssistantModal />
            <CreateUserModal />
        </>
    );
};

