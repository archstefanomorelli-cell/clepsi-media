// Lo studio di esempio del sito (Villa Rossi, Scuola Brera, Uffici Lambrate, Loft Navigli) per il finto backend mock_nuovo.js.
// Costo di una giornata 320 €. Stati come sul sito: VRO in attivo, SBR margine stretto, ULA in perdita, LNA appena iniziata.
const PERSONE = ['Luca Bianchi', 'Sara Conti', 'Paolo Greco'];
function opzioni(extra = {}) {
  return {
    studio: { nome: 'Studio di esempio', io: 'Marta Rossi', persone: PERSONE },
    commesse: [
      { nome: 'Villa Rossi', sigla: 'VRO', colore: '#D4FF3A', tipo: 'nuovaCostruzione', giornate: 24, mezzeSettimana: 7, variantiPrima: 7,
        persone: [['Marta Rossi', 6], ['Sara Conti', 12], ['Paolo Greco', 6]], giornateFasi: [9, 15, 0],
        fasi: [{ nome: 'Progetto definitivo', cent: 480000, stato: 'done' }, { nome: 'Progetto esecutivo', cent: 900000, stato: 'almost' }, { nome: 'Direzione lavori', cent: 420000, stato: 'todo' }] },
      { nome: 'Scuola Brera', sigla: 'SBR', colore: '#9B8CFF', tipo: 'ristrutturazione', giornate: 20, mezzeSettimana: 6,
        persone: [['Luca Bianchi', 12], ['Marta Rossi', 5], ['Sara Conti', 3]], giornateFasi: [6, 12, 2], budgetFasi: [6, 10, 9],
        fasi: [{ nome: 'Fattibilità tecnico-economica', cent: 260000, stato: 'done' }, { nome: 'Progetto esecutivo', cent: 430000, stato: 'almost' }, { nome: 'Esecuzione dei lavori', cent: 390000, stato: 'started' }] },
      { nome: 'Uffici Lambrate', sigla: 'ULA', colore: '#6FD3FF', tipo: 'ristrutturazione', giornate: 31, mezzeSettimana: 17, variantiPrima: 10,
        persone: [['Sara Conti', 13], ['Luca Bianchi', 10], ['Marta Rossi', 5], ['Paolo Greco', 3]], giornateFasi: [8, 17, 6], budgetFasi: [7, 12, 8],
        variantiSettimane: [['2026-09-21', 3], ['2026-10-12', 4], ['2026-11-02', 5]],
        fasi: [{ nome: 'Progetto definitivo', cent: 240000, stato: 'done' }, { nome: 'Progetto esecutivo', cent: 400000, stato: 'done' }, { nome: 'Direzione lavori', cent: 260000, stato: 'half' }] },
      { nome: 'Loft Navigli', sigla: 'LNA', colore: '#FF9ECF', tipo: 'interni', giornate: 2, mezzeSettimana: 3,
        persone: [['Paolo Greco', 2]], giornateFasi: [2, 0],
        fasi: [{ nome: 'Progetto', cent: 520000, stato: 'todo' }, { nome: 'Direzione lavori', cent: 210000, stato: 'todo' }] },
    ],
    ...extra,
  };
}
module.exports = { opzioni, PERSONE };
// la settimana 46 del sito (funzioni/settimana-studio): Titolare, Socio, Dipendente, Collaboratore
module.exports.GRIGLIA = {
  'Marta Rossi': ['VRO', 'VRO', 'ULA', 'ULA', 'VRO', 'SBR', 'ULA', 'ULA', 'S', 'S'],
  'Luca Bianchi': ['SBR', 'SBR', 'SBR', 'ULA', 'ULA', 'ULA', 'SBR', 'SBR', 'ULA', 'LNA'],
  'Sara Conti': ['ULA', 'ULA', 'ULA', 'ULA', 'VRO', 'VRO', 'ULA', 'ULA', 'VRO', 'VRO'],
  'Paolo Greco': ['LNA', 'LNA', 'VRO', 'VRO', '-', '-', 'LNA', 'ULA', 'ULA', 'ULA'],
};
