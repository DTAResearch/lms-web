"use client";

import { useState } from "react";
import Image from "next/image";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/constants/URL";
import axiosInstance from "@/lib/Api-Instance";
import { toast } from "sonner";
import { Models } from "../admin/Assistant-Ai-Page";
import { ActionTooltip } from "../action-tooltip";

interface ModelCardProps {
  model: Models;
  canEdit: boolean;
  onModelUpdated?: (modelId: string, isActive: boolean) => void;
}

const ModelCard = ({ model, canEdit, onModelUpdated }: ModelCardProps) => {
  const [isActive, setIsActive] = useState(model.is_active);
  const [isLoading, setIsLoading] = useState(false);

  const handleToggle = async () => {
    const url = `${API_BASE_URL}/models/toggle/is-active/${model.id}`;
    setIsLoading(true);

    try {
      const response = await axiosInstance.put(url);
      if (response.status === 200) {
        const data = response.data.data;
        setIsActive(data.is_active);

        // Call the callback to update parent component state if provided
        if (onModelUpdated) {
          onModelUpdated(model.id, data.is_active);
        }

        toast.success(`Model ${data.is_active ? 'activated' : 'deactivated'} successfully`);
      }
    } catch (error) {
      console.error("Error toggling model status:", error);
      toast.error("Failed to update model status");
      // Revert the UI state on error
      setIsActive(model.is_active);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="group relative">
      <div className={cn(
        "bg-white dark:bg-gray-750 rounded-xl p-4 shadow-sm border border-gray-100 dark:border-gray-700",
        "hover:shadow-md hover:border-gray-200 dark:hover:border-gray-600 transition-all duration-200",
        "flex flex-col items-center h-full",
        canEdit && "cursor-pointers"
      )}>
        <div className="mb-4">
          <div className="w-28 h-28 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-700 backdrop-blur-sm flex items-center justify-center">
            {isActive ? (
              <a
                href={`https://chat.hoctiep.com/?models=${model.id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full h-full flex items-center justify-center cursor-pointer"
              >
                <Image
                  src={model.image_url || "/images/logo.png"}
                  alt={model.title}
                  width={112}
                  height={112}
                  className="object-cover rounded-full group-hover:scale-105 transition-transform duration-300"
                  priority
                  unoptimized
                />
              </a>
            ) : (
              <Image
                src={model.image_url || "/images/logo.png"}
                alt={model.title}
                width={112}
                height={112}
                className="object-cover rounded-full opacity-50"
                priority
                unoptimized
              />
            )}
          </div>
        </div>

        <h3 className="text-lg font-medium text-gray-800 dark:text-gray-100 text-center mb-1 group-hover:text-sky-600 dark:group-hover:text-sky-400 transition-colors">
          {model.title}
        </h3>

        <p className="text-sm text-gray-500 dark:text-gray-400 text-center line-clamp-2">
          {model.description || "No description available"}
        </p>

        {canEdit && (
          <div className="flex items-center mt-3">
            <div
              className="absolute bottom-2 right-2"
              onClick={(e) => e.stopPropagation()}
            >
              <ActionTooltip label="Bật tắt model" side="top">
                <div className="flex items-center gap-2">
                  <Switch
                    id={`switch-${model.id}`}
                    checked={isActive}
                    disabled={isLoading}
                    className={cn(
                      isActive ? "!bg-emerald-300 cursor-pointer" : "bg-gray-200 dark:bg-gray-700 cursor-pointer",
                      isLoading && "opacity-50 cursor-not-allowed"
                    )}
                    onCheckedChange={handleToggle}
                  />
                </div>
              </ActionTooltip>
            </div>
          </div>
        )}

        {model.author && (
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-3">
            Created by {model.author}
          </p>
        )}
      </div>
    </div>
  );
};

export default ModelCard;