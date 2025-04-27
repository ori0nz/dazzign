import {  useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Flame } from 'lucide-react';
import Button from '../components/ui/Button';

interface Idea {
  id: number;
  keyword: string;
  imageUrl: string;
  attributes: string[];
  description: string;
  popularity: number;
  specJson: Record<string, string[]>;
}

const IDEAS: Idea[] = [
  {
    id: 10000,
    keyword: "魔物獵人",
    imageUrl: "https://resize-image.vocus.cc/resize?compression=6&norotation=true&url=https%3A%2F%2Fimages.vocus.cc%2F571b777e-7636-472a-9679-54f838af84b9.png&width=740&sign=m2dHqIkA5hYzvOpX0ZMJkDriCHSZlH0LOBuJkC1RcA8",
    attributes: ["火龍", "雷狼龍", "揮舞大劍的獵人"],
    description: " 魔物獵人系列獨特的部位破壞與四人連線共同討伐巨大魔物的特性蔚為風潮，發展為系列作一貫的風格特色。",
    popularity: 95,
    specJson: 
      {
        "color": ["Black", "Grey", "Orange", "Red", "Brown", "Metallic"],
        "style": ["Futuristic", "Rugged", "Industrial", "Fantasy"],
        "shape": ["Mid-Tower", "Boxy", "Angled", "Tough"],
        "material": ["Metal", "Tempered Glass", "Acrylic", "Plastic", "Carbon Fiber"],
        "ventilation": ["Mesh Front", "Side Vents", "Top Vents", "Heavy Venting"],
        "lighting": ["RGB Lights", "Ambient Glow", "LED Strips"],
        "features": ["Custom Hunter Design", "Monster Artworks", "Weapon Embellishments", "Rugged Armor Details"],
        "environment": ["Hunter's Workshop", "Fantasy Lab", "Wild Terrain", "Dark Forest"],
        "modifiers": ["Large Side Panel", "Monster Heads", "Weapon Details", "LED Monster Eyes", "Detailed Emblems"]
      }
    
  },
  {
    id: 10001,
    keyword: "SD鋼彈",
    imageUrl: "https://p2.bahamut.com.tw/B/2KU/85/42d73bfc8e37b957e10bfae8471ttl55.PNG",
    attributes: ["元祖SD鋼彈", "BB戰士", "SD戰國傳"],
    description: "SD鋼彈（Super Deformed Gundam）是指鋼彈系列作品當中登場的機械與人物，將其頭部誇張化，手腳縮小成為二頭身比例的角色，以及使用SD機械／人物所製作的商品群之總稱。",
    popularity: 85,
    specJson: {
      "color": ["Red", "Blue", "Green", "Yellow", "White", "Black"],
      "style": ["Classic", "Modern", "Retro", "Futuristic"],
      "shape": ["Boxy", "Angled", "Rounded", "Tough"],
      "material": ["Metal", "Plastic", "Carbon Fiber", "Glass"],
      "features": ["Custom Design", "Monster Artworks", "Weapon Embellishments", "Rugged Armor Details"]
    }
  },
  {
    id: 3,
    keyword: "超級瑪利歐", 
    imageUrl: "https://shopee.tw/blog/wp-content/uploads/2019/01/%E6%96%B0-%E8%B6%85%E7%B4%9A%E7%91%AA%E5%88%A9%E6%AD%90%E5%85%84%E5%BC%9F-u.jpg",
    attributes: ["水管工", "路易吉", "義大利籍美國人","大鼻子","最愛用槌子"],
    description: "紅色帽子配藍色吊帶工作褲，加上標誌性的鬍子。 他就是永遠生氣勃勃又開朗的瑪利歐。 跑跑跳跳，利用超級蘑菇提升力量！ 他善用各種動作和道具，在世界中冒險。",
    popularity: 75,
    specJson: {
      "color": ["Red", "Blue", "Green", "Yellow", "White", "Black"],
      "style": ["Classic", "Modern", "Retro", "Futuristic"],
      "shape": ["Boxy", "Angled", "Rounded", "Tough"],
      "material": ["Metal", "Plastic", "Carbon Fiber", "Glass"],
      "features": ["Custom Design", "Monster Artworks", "Weapon Embellishments", "Rugged Armor Details"],
    }
  },
  {
    id: 4,
    keyword: "咖波",
    imageUrl: "https://im2.book.com.tw/image/getImage?i=https://www.books.com.tw/img/N01/378/09/N013780916_t_03.jpg&v=66fa78fb",
    attributes: ["貓貓蟲", "愛吃肉", "capoo"],
    description: "外表像貓又像蟲的卡通人物，於2014年由台灣藝術家亞拉所創造。 其設定為像貓又像蟲藍色小怪物，平時擁有6隻腳，數量會視情況變化，暴力獵奇又萌萌可愛，最愛吃肉，還有咬手手。",
    popularity: 66,
    specJson: {
      "color": ["Red", "Blue", "Green", "Yellow", "White", "Black"],
      "style": ["Classic", "Modern", "Retro", "Futuristic"],
      "shape": ["Boxy", "Angled", "Rounded", "Tough"],
      "material": ["Metal", "Plastic", "Carbon Fiber", "Glass"],
      "features": ["Custom Design", "Monster Artworks", "Weapon Embellishments", "Rugged Armor Details"],
    }
  },
  {
    id: 5,
    keyword: "好想兔",
    imageUrl: "https://stickershop.line-scdn.net/stickershop/v1/product/29515/IOS/main_animation@2x.png",
    attributes: ["好想兔", "謙謙創意"],
    description: "好想兔真情外露~不只會夭飽吵.真實的感情自然的表現通通讓你真情的流露.一絲不掛的完整幫你傳達(´・ω・``)",
    popularity: 63, 
    specJson: {
      "color": ["Red", "Blue", "Green", "Yellow", "White", "Black"],
      "style": ["Classic", "Modern", "Retro", "Futuristic"],
      "shape": ["Boxy", "Angled", "Rounded", "Tough"],
      "material": ["Metal", "Plastic", "Carbon Fiber", "Glass"],
      "features": ["Custom Design", "Monster Artworks", "Weapon Embellishments", "Rugged Armor Details"],
    }
  },
  {
    id: 6,
    keyword: "玩具總動員",
    imageUrl: "https://www.nornsblog.com/wp-content/uploads/DBDEC9255A06D3829F1CA8BB79022ADBB533FA51153204A9A18CFA7E6DCC75AF.png",
    attributes: ["胡迪", "巴斯光年", "反鬥奇兵", "熊抱哥", "眼怪"],
    description: "傳統牛仔玩偶「胡迪」（Woody）是男孩安弟（Andy）最喜歡的玩具，可是熱門玩具「巴斯光年」來了之後讓胡迪失寵。",
    popularity: 59,
    specJson: {
      "color": ["Yellow", "Red", "Blue", "Green", "Brown", "Orange", "Purple", "White"],
      "style": ["Cartoonish", "Playful", "Whimsical", "Vibrant", "Childlike", "3D Animation"],
      "shape": ["Toy-Like", "Blocky", "Rounded", "Exaggerated Features", "Stylized"],
      "material": ["Plastic", "Wood", "Fabric", "Painted Textures"],
      "ventilation": ["No specific ventilation"],
      "lighting": ["Bright Lighting", "Colorful Lighting Effects", "Soft Shadows"],
      "features": ["Toy Characters", "Playful Animations", "Exaggerated Movements", "Friendly Faces", "Imaginative World"],
      "environment": ["Toy Room", "Playground", "Child's Bedroom", "Playful Settings"],
      "modifiers": ["Large Toy Figures", "Familiar Everyday Objects", "Action-Packed Scenes", "Character Interactions", "Anthropomorphized Toys"]
    }
  },
  {
    id: 7,
    keyword: "懶得鳥你",
    imageUrl: "https://scontent.ftpe12-2.fna.fbcdn.net/v/t39.30808-6/462752602_3670010389918647_6316033045103512133_n.jpg?_nc_cat=109&ccb=1-7&_nc_sid=127cfc&_nc_ohc=8vNSvoJUkmcQ7kNvwGoHTZR&_nc_oc=Adm6wWqNsrv9x5FSnpGgDsSJd3geiRoXN8jcIxpSPh8imY5Q7QKR-XqniDUoU21zYgOlBaB7yWZx41fwvbMRh8P0&_nc_zt=23&_nc_ht=scontent.ftpe12-2.fna&_nc_gid=R6QhaoSlL1AWTWx91qQICg&oh=00_AfEhLIW_srbwiWWv4ZFI3rf7CJfdaaFg6vss4dL8jojVZQ&oe=68136EC1",
    attributes: ["懶得鳥", "直白妹", "胖企鵝", "秀吉", "黃小姬"],
    description: "懶得”鳥”你以超級敷衍的特色及可以讓人理智線斷掉的神煩貼圖，深受年輕人的喜歡，敷衍、激動、KUSO的LINE貼圖在日本與台灣刮起一陣狂熱旋風，甚至在日本LINE貼圖下載量榮登第一名。",
    popularity: 50,
    specJson: {
      "color": ["Black", "Gray", "Muted Tones", "White"],
      "style": ["Minimalist", "Casual", "Laid-back", "Nonchalant", "Lazy", "Apathy"],
      "shape": ["Simple", "Uncomplicated", "Relaxed"],
      "material": ["Cotton", "Denim", "Leather", "Basic Fabrics"],
      "ventilation": ["No emphasis on airflow", "Closed-off"],
      "lighting": ["Soft", "Dim", "Natural Light"],
      "features": ["Comfortable Seating", "Casual Clothing", "Relaxed Pose", "Unbothered Attitude"],
      "environment": ["Home", "Couch", "Bedroom", "Coffee Shop", "Casual Outdoors"],
      "modifiers": ["No Effort", "Low-Key", "Indifferent Expressions"]
    }
  },
  {
    id: 8,
    keyword: "line friends",
    imageUrl: "https://www.linefriends.com/static/media/ip_lf_img01.5254b5b4c4d23dcc82aa.png",
    attributes: ["熊大", "兔兔", "莎莉", "詹姆士","饅頭人", "可妮", "布朗", ],
    description: "熊大與好友日常》以大家熟知的角色們作為中心，包括熊大（BROWN）、兔兔（CONY）、莎莉（SALLY）、詹姆士（JAMES）等 11 位角色都以 3D 動畫呈現，並以都市的日常生活作為背景，在溫馨的社區小咖啡店裡，看這些充滿個性與魅力的角色們，將會展開怎樣的動畫故事。",
    popularity: 86,
    specJson: {
      "color": ["Brown", "White", "Beige", "Pink", "Yellow"],
      "style": ["Cute", "Cartoonish", "Playful", "Kawaii", "Simple"],
      "shape": ["Round", "Soft", "Chibi", "Simplified Features"],
      "material": ["Soft Fabric", "Plush", "Cotton", "Polyester"],
      "ventilation": ["No specific ventilation", "Minimal emphasis on details"],
      "lighting": ["Bright", "Pastel Lighting", "Soft", "Warm"],
      "features": ["Character-based", "Friendly Faces", "Simple Shapes", "Expressive Eyes", "Hugging or Friendly Gestures"],
      "environment": ["Bright Room", "Playful Background", "Casual Setting", "Happy Atmosphere"],
      "modifiers": ["Stuffed Toys", "Plushie Design", "Cute Accessories", "Simple Patterns"]
    }
  },
  {
    id: 9,
    keyword: "史努比",
    imageUrl: "https://upload.wikimedia.org/wikipedia/zh/c/c8/Snoopy%28The_Peanuts%29.jpg",
    attributes: ["relaxation", "interior", "hobby"],
    description: "牠是《花生漫畫》裡代表性的卡通形象之一，有著充滿自信、喜愛天馬行空幻想的個性，以及許多趣味的擬人化表現演出",
    popularity: 30,
    specJson: {
      "color": ["Black", "White", "Yellow", "Red"],
      "style": ["Cartoonish", "Playful", "Minimalist", "Vintage"],
      "shape": ["Mid-Tower", "Compact", "Boxy", "Round Edges"],
      "material": ["Plastic", "Metal", "Acrylic"],
      "ventilation": ["Mesh Front", "Side Vents", "Top Vents"],
      "lighting": ["Soft LED Glow", "Simple Lighting"],
      "features": ["Snoopy Character Graphics", "Peanuts Theme", "Simple Illustrations", "Character Poses"],
      "environment": ["Cozy Living Room", "Casual Gaming Desk", "Vintage Styled Room"],
      "modifiers": ["Snoopy Face", "Woodstock Figure", "Peanuts Logo", "Red Doghouse Design", "Simple Color Blocks"]
    }
  }
];

const IdeaPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const ideas = IDEAS;

  const handleNewImage = () => {
    navigate('/create');
  };

  const handleIdeaClick = (idea: Idea) => {
    navigate('/create', {
      state: {
        prompt: idea.description,
        // attributes: idea.attributes,
        keyword: idea.keyword,
        specJson: idea.specJson
      }
    });
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
        <h1 className="text-3xl font-bold text-gray-900"></h1>
        {/* <Button 
          variant="primary" 
          size="lg"
          onClick={handleNewImage}
          className="transition-transform hover:scale-105"
        >
          {t('home.newImage')}
        </Button> */}
      </div>

      <div className="grid auto-rows-[280px] grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {ideas.map((idea) => (
          <div
            key={idea.id}
            className={`group relative overflow-hidden rounded-xl bg-white shadow-sm transition-all duration-300 hover:shadow-lg ${getGridSpan(idea.popularity)} cursor-pointer`}
            onClick={() => handleIdeaClick(idea)}
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