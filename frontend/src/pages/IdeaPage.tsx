import React, { useState,useMemo, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ImageNode } from '../models/types';
import { imageService } from '../services/imageService';
import ImagePreview from '../components/image/ImagePreview';
import { useTranslation } from 'react-i18next';
import { Search, TrendingUp, Flame } from 'lucide-react';
import Button from '../components/ui/Button';

interface Idea {
  id: number;
  keyword: string;
  imageUrl: string;
  attributes: string[];
  description: string;
  popularity: number;
}

const IDEAS: Idea[] = [
  {
    id: 10000,
    keyword: "魔物獵人",
    imageUrl: "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/582010/header.jpg?t=1734656748",
    attributes: ["火龍", "雷狼龍", "揮舞大劍的獵人"],
    description: " 魔物獵人系列獨特的部位破壞與四人連線共同討伐巨大魔物的特性蔚為風潮，發展為系列作一貫的風格特色。",
    popularity: 95
  },
  {
    id: 10001,
    keyword: "SD鋼彈",
    imageUrl: "https://p2.bahamut.com.tw/B/2KU/85/42d73bfc8e37b957e10bfae8471ttl55.PNG",
    attributes: ["元祖SD鋼彈", "BB戰士", "SD戰國傳"],
    description: "SD鋼彈（Super Deformed Gundam）是指鋼彈系列作品當中登場的機械與人物，將其頭部誇張化，手腳縮小成為二頭身比例的角色，以及使用SD機械／人物所製作的商品群之總稱。",
    popularity: 85
  },
  {
    id: 3,
    keyword: "Sustainable Garden",
    imageUrl: "https://images.pexels.com/photos/1105019/pexels-photo-1105019.jpeg",
    attributes: ["nature", "eco-friendly", "hobby"],
    description: "Create your own urban oasis with sustainable practices. Transform spaces into green havens.",
    popularity: 75
  },
  {
    id: 4,
    keyword: "Digital Art",
    imageUrl: "https://images.pexels.com/photos/2168831/pexels-photo-2168831.jpeg",
    attributes: ["creative", "technology", "modern"],
    description: "Express yourself through digital creativity. Blend technology with artistic vision.",
    popularity: 90
  },
  {
    id: 5,
    keyword: "Home Office",
    imageUrl: "https://images.pexels.com/photos/4348404/pexels-photo-4348404.jpeg",
    attributes: ["workspace", "productivity", "design"],
    description: "Design your perfect remote workspace for maximum productivity and comfort.",
    popularity: 88
  },
  {
    id: 6,
    keyword: "Meditation Space",
    imageUrl: "https://images.pexels.com/photos/3822622/pexels-photo-3822622.jpeg",
    attributes: ["wellness", "mindfulness", "interior"],
    description: "Create a peaceful sanctuary at home for mindfulness and relaxation.",
    popularity: 82
  },
  {
    id: 7,
    keyword: "Cooking Studio",
    imageUrl: "https://images.pexels.com/photos/1267320/pexels-photo-1267320.jpeg",
    attributes: ["culinary", "hobby", "lifestyle"],
    description: "Transform your kitchen into a culinary workshop. Master the art of cooking.",
    popularity: 78
  },
  {
    id: 8,
    keyword: "Fitness Corner",
    imageUrl: "https://images.pexels.com/photos/4162485/pexels-photo-4162485.jpeg",
    attributes: ["health", "exercise", "lifestyle"],
    description: "Build your personal workout space for a healthier lifestyle.",
    popularity: 86
  },
  {
    id: 9,
    keyword: "Reading Nook",
    imageUrl: "https://images.pexels.com/photos/2079249/pexels-photo-2079249.jpeg",
    attributes: ["relaxation", "interior", "hobby"],
    description: "Design a cozy corner for your books and peaceful reading moments.",
    popularity: 80
  }
];

const IdeaPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const ideas = IDEAS;

  const handleNewImage = () => {
    navigate('/create');
  };

  const getGridSpan = (popularity: number): string => {
    if (popularity >= 90) return 'md:col-span-2 md:row-span-2';
    if (popularity >= 85) return 'md:col-span-2';
    return '';
  };

  const getPopularityColor = (popularity: number): string => {
    if (popularity >= 90) return 'text-red-400';
    if (popularity >= 85) return 'text-orange-400';
    if (popularity >= 80) return 'text-yellow-400';
    return 'text-gray-400';
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">{t('ideas.title')}</h1>
        <Button 
          variant="primary" 
          size="lg"
          onClick={handleNewImage}
          className="transition-transform hover:scale-105"
        >
          {t('ideas.newImage')}
        </Button>
      </div>

      <div className="grid auto-rows-[280px] grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {ideas.map((idea) => (
          <div
            key={idea.id}
            className={`group relative overflow-hidden rounded-xl bg-white shadow-sm transition-all duration-300 hover:shadow-lg ${getGridSpan(idea.popularity)}`}
          >
            <div className="absolute inset-0">
              <img
                src={idea.imageUrl}
                alt={idea.keyword}
                className="h-full w-full object-cover object-center transition-transform duration-300 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent">
                <div className="absolute bottom-0 left-0 right-0 p-6">
                  <div className="mb-2 flex items-center justify-between">
                    <h3 className="text-xl font-bold text-white">
                      {idea.keyword}
                    </h3>
                    <div className={`flex items-center gap-1 ${getPopularityColor(idea.popularity)}`}>
                      <Flame className="h-5 w-5" />
                      <span className="font-medium">{idea.popularity}</span>
                    </div>
                  </div>
                  <p className="mb-4 line-clamp-2 text-sm text-gray-200">
                    {idea.description}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {idea.attributes.map((attribute, index) => (
                      <span
                        key={index}
                        className="rounded-full bg-white/20 px-3 py-1 text-xs font-medium text-white backdrop-blur-sm transition-colors hover:bg-white/30"
                      >
                        {attribute}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default IdeaPage;