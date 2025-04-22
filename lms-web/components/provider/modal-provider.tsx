"use client";
import { useEffect, useState } from "react";
import { CreateAssistant } from "../modals/create-assitant";

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
            <CreateAssistant />
        </>
    );
};

