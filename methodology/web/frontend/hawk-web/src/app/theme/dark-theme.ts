import { Theme } from './symbols';

export const darkTheme: Theme = {
  name: 'dark',
  properties: {
    '--background': '#1F2125',
    '--content-background': 'linear-gradient(145deg, #262627, #454750)',
    '--on-background': '#fff',
    '--text-color': '#fff',
    '--primary': 'darkorange',
    '--on-primary': '#fff',
    '--table-odd-background': '#b3b9b8',
    '--table-odd-color': '#000',
    '--table-even-background': '#FFF',
    '--table-even-color': '#000',
    '--box-shadow-first-color': '#101114',
    '--box-shadow-second-color': '#24252a',
    '--button-shadow-first-color': '16, 17, 20',
    '--button-shadow-second-color': '36, 37, 42',
    '--content-box-shadow-first-color': '167, 168, 171',
    '--content-box-shadow-second-color': '36, 37, 42',
    '--content-box-shadow-third-color': '167, 168, 171',
    '--content-box-shadow-fourth-color': '36, 37, 42',
    '--content-box-shadow-fifth-color': '36, 37, 42',
    '--scroll-bar-background-color': '#000000',
    '--search-icon-color': '#495057'
  }
};
