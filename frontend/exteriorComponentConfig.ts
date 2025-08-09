// config/exteriorComponentConfig.ts
import { ComponentEntry } from '../types/component';

const exteriorComponentConfig: Record<string, ComponentEntry> = {
  Rear_Bumper: {
    name: 'Rear Bumper',
    image: require('../assets/rearbumper.jpg'),
    parts: ['Rear'],
    referenceImages: [
      require('../assets/reference/rearbump.jpg'),
    ],
  },
  Lettering: {
    name: 'Lettering',
    image: require('../assets/lettering.jpg'),
    parts: ['Front'],
    referenceImages: [
      require('../assets/reference/lettering.jpg'),
    ],
  },
  Front_Door_Finisher: {
    name: 'Front Door Finisher',
    image: require('../assets/fdf.jpg'),
    parts: ['Left Forward','Right Forward'],
    referenceImages: [
      require('../assets/reference/leftfdf.jpg'),
      require('../assets/reference/rightfdf.jpg'),
    ],
  },
};

export default exteriorComponentConfig;
