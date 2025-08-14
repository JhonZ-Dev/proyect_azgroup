import { definePreset } from '@primeng/themes';
import Aura from '@primeng/themes/aura';


const MyPreset = definePreset(Aura, {
    semantic: {
        primary: {
            50: '{zinc.50}',
            100: '{zinc.100}',
            200: '{zinc.200}',
            300: '{zinc.300}',
            400: '{zinc.400}',
            500: '{zinc.500}',
            600: '{zinc.600}',
            700: '{zinc.700}',
            800: '{zinc.800}',
            900: '{zinc.900}',
            950: '{zinc.950}'
        },
        colorScheme: {
            light: {
                primary: {
                    color: '{zinc.950}',
                    inverseColor: '#ffffff',
                    hoverColor: '{zinc.900}',
                    activeColor: '{zinc.800}'
                },
                highlight: {
                    background: '{zinc.950}',
                    focusBackground: '{zinc.700}',
                    color: '#ffffff',
                    focusColor: '#ffffff'
                }
            },
            dark: {
                primary: {
                    color: '{zinc.50}',
                    inverseColor: '{zinc.950}',
                    hoverColor: '{zinc.100}',
                    activeColor: '{zinc.200}'
                },
                highlight: {
                    background: 'rgba(250, 250, 250, .16)',
                    focusBackground: 'rgba(250, 250, 250, .24)',
                    color: 'rgba(255,255,255,.87)',
                    focusColor: 'rgba(255,255,255,.87)'
                }
            }
        }
    }
});

const customPreset = definePreset(Aura, {
    semantic: {
      primary: {
        50: '{pink.50}',
        100: '{pink.100}',
        200: '{pink.200}',
        300: '{pink.300}',
        400: '{pink.400}',
        500: '{pink.500}',
        600: '{pink.600}',
        700: '{pink.700}',
        800: '{pink.800}',
        900: '{pink.900}',
        950: '{pink.950}',
      },
      colorScheme: {
        light: {
          primary: {
            color: '{pink.800}',
            inverseColor: '#ffffff',
            hoverColor: '{pink.900}',
            activeColor: '{pink.800}',
          },
          highlight: {
            background: '{pink.950}',
            focusBackground: '{pink.700}',
            color: '#ffffff',
            focusColor: '#ffffff',
          },
        },
        dark: {
          primary: {
            color: '{pink.50}',
            inverseColor: '{pink.950}',
            hoverColor: '{pink.100}',
            activeColor: '{pink.200}',
          },
          highlight: {
            background: 'rgba(250, 250, 250, .16)',
            focusBackground: 'rgba(250, 250, 250, .24)',
            color: 'rgba(255,255,255,.87)',
            focusColor: 'rgba(255,255,255,.87)',
          },
        },
      },
    },
  });
  export default customPreset;
