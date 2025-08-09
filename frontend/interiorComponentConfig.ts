// config/componentConfig.ts
import { ComponentEntry } from '../types/component';

const interiorComponentConfig: Record<string, ComponentEntry> = {
  Tyre: {
    name: 'Tyre',
    image: require('../assets/tyre.jpg'),
    parts: ['Left Front', 'Right Rear', 'Left Rear', 'Right Front'],
    referenceImages: [
      require('../assets/reference/tyreleftfront.jpg'),
      require('../assets/reference/tyrerightrear.jpg'),
      require('../assets/reference/tyreleftrear.jpg'),
      require('../assets/reference/tyrerightfront.jpg'),
    ],
  },
  Brake_Caliper: {
    name: 'Brake Caliper',
    image: require('../assets/brake.jpg'),
    parts: ['Left Front', 'Right Rear', 'Left Rear', 'Right Front'],
    referenceImages: [
      require('../assets/reference/brakeleftfront.jpg'),
      require('../assets/reference/brakerightrear.jpg'),
      require('../assets/reference/brakeleftrear.jpg'),
      require('../assets/reference/brakerightfront.jpg'),
    ],
  },
  Sidewall_Ingot: {
    name: 'Sidewall Ingot',
    image: require('../assets/ingot.jpg'),
    parts: ['Left Rear', 'Right Rear'],
    referenceImages: [
      require('../assets/reference/ingotleftrear.jpg'),
      require('../assets/reference/ingotrightrear.jpg'),
    ],
  },
  Smile_Line: {
    name: 'Smile Line',
    image: require('../assets/5.jpg'),
    parts: ['Single View'],
    referenceImages: [require('../assets/reference/5.jpg')],
  },
  Doorpad: {
    name: 'Doorpad',
    image: require('../assets/doorpad.jpg'),
    parts: ['Left Front', 'Right Front'],
    referenceImages: [
      require('../assets/reference/doorpadleftfront.jpg'),
      require('../assets/reference/doorpadrightfront.jpg'),
    ],
  },
};

export default interiorComponentConfig;
