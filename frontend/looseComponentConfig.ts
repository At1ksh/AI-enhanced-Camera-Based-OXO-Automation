// config/looseComponentConfig.ts
import { ComponentEntry } from '../types/component';

const looseComponentConfig: Record<string, ComponentEntry> = {
  Steering: {
    name: 'Steering',
    image: require('../assets/steering.jpg'),
    parts: ['Drivers Side'],
    referenceImages: [
      require('../assets/reference/steering.jpg'),
    ],
  },
  Upper_Door_Speaker: {
    name: 'Upper Door Speaker',
    image: require('../assets/upperdoorspeaker.jpg'),
    parts: ['Right Front Door','Left Front Door','Right Rear Door','Left Rear Door'],
    referenceImages: [
      require('../assets/reference/rightfrontupperdoorspeaker.jpg'),
      require('../assets/reference/leftfrontupperdoorspeaker.jpg'),
      require('../assets/reference/rightreardoorspeaker.jpg'),
      require('../assets/reference/leftreardoorspeaker.jpg'),
    ],
  },
};

export default looseComponentConfig;
