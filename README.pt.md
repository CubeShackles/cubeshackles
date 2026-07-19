[English](./README.md) | [Português](./README.pt.md)

# CubeShackles

**Repositório guarda-chuva canónico — a fonte institucional da verdade para
a plataforma CubeShackles.**

**Proprietário: CubeShackles (liderado pelo fundador).** A narrativa da
plataforma, a doutrina e a autoridade de merge são lideradas pelo fundador.
As ferramentas de programação com IA podem assistir a engenharia; não são
autoras nem proprietárias da CubeShackles. Ver
[`governance/policies/authorship-and-tooling.md`](governance/policies/authorship-and-tooling.md).

> Este repositório **não** é a implementação do protocolo. Não contém código
> de protocolo, modelos de IA, lógica de fraude, ferramentas para reguladores
> nem segredos de produção. É a descrição autorizada do que é a CubeShackles,
> de como os seus 55 repositórios se encaixam, dos padrões a que cada
> componente está sujeito e da governança que mantém o ecossistema honesto.

---

## O que é a CubeShackles

A CubeShackles é **infraestrutura financeira soberana nativa de Angola** —
uma plataforma de liquidação e coordenação determinística construída para
ser o sistema operativo financeiro de uma jurisdição que está a construir os
seus trilhos a partir de princípios fundamentais, em vez de herdar
arquitetura bancária legada.

Não é um clone de blockchain, um projeto de token ou uma aplicação de
pagamentos. É concebida como infraestrutura soberana de grau regulatório,
organizada em torno de duas primitivas:

- **Cube** — a unidade canónica de estado: um registo determinístico,
  endereçado por hash, imutável, de atividade económica e sensível à
  identidade.
- **Shackle** — a lógica de restrição e compromisso que liga Cubes entre si
  segundo regras: condições de liquidação, atestações de identidade,
  obrigações de validadores e (em fases posteriores) mecanismos de política
  assistidos por IA que permanecem isolados da execução crítica para o
  consenso.

Em conjunto, a lógica Cube + Shackle disponibiliza:

- liquidação determinística com ordenação causal baseada em DAG,
- transações sensíveis à identidade com trilhas de auditoria de grau
  regulatório,
- coordenação de validadores com regras definidas de exclusão e atribuição,
- uma cadeia de controlo de finanças institucionais (normalização →
  conformidade → compensação → liquidação → livro-razão),
- uma camada de IA consultiva isolada do consenso, incapaz de o corromper,
- infraestrutura de tokenização e de ativos do mundo real,
- acesso offline-first para ambientes de baixa conectividade,
- e um percurso de longo prazo rumo a infraestrutura de computação nativa em
  IA, agnóstica de hardware.

**O AOA (Kwanza angolano) é a moeda de liquidação nativa** em todos os
contratos de interoperabilidade e semânticas de protocolo.

---

## Estado da plataforma (julho de 2026)

| Marco | Estado |
|---|---|
| `RC2_FREEZE` — núcleo financeiro congelado | **Completo** |
| `AI_NATIVE_M5` — plataforma de IA com 11 agentes, fronteira apenas consultiva reforçada | **Completo** |
| `PLATFORM_ALPHA_1` — base institucional, suite completa de gates a passar | **Completo** (2026-06-30) |
| Candidato a Congelamento de Funcionalidades — modo de manutenção e garantia | **Ativo** |
| `PLATFORM_BETA_1` — linguagem de design unificada do SO em todas as aplicações | **Alvo** |
| Piloto Angola — corredor de implantação controlada | **Planeado** |

---

## Postura de design

A CubeShackles é concebida como infraestrutura soberana de longo prazo, não
como um conjunto de funcionalidades de consumo. As propriedades orientadoras
são:

- **Execução determinística** — as mesmas entradas produzem as mesmas saídas
  em todo o lado, sempre.
- **Estado replicável** — cada transição de estado é reproduzível a partir do
  histórico ordenado.
- **Auditabilidade de grau regulatório** — cada ação de validador é
  observável, atribuível e reconstruível por um regulador autorizado.
- **Isolamento da IA** — os componentes de IA informam; nunca corrompem o
  estado crítico para o consenso.
- **Cadeia de controlo institucional** — a conformidade condiciona a
  compensação; a compensação condiciona a liquidação; nenhuma fronteira pode
  ser contornada.
- **Computação agnóstica de hardware** — concebida para migrar entre Nvidia
  CUDA, AMD ROCm, ARM, RISC-V, FPGA e futuros Cube Silicon / Shackle Silicon.
- **Implantação offline-first em Angola** — a conectividade é tratada como
  intermitente por defeito.
- **Liquidação nativa em AOA** — o Kwanza angolano é de primeira classe em
  toda a semântica do protocolo.
- **Modularidade orientada à segurança** — fronteiras de confiança estritas
  entre camadas; atravessar uma fronteira exige autenticação, validação e
  registo (logging).

---

## Doutrina de honestidade

Este repositório descreve um sistema **parcialmente implementado e
parcialmente planeado.** Usamos linguagem precisa deliberadamente:

- **"implementa" / "disponibiliza" / "ativo"** — existe e é exercitado por
  testes.
- **"concebido para" / "destinado a" / "estruturado"** — uma direção
  comprometida, com estrutura em disco, ainda não integrada na cadeia de
  gates de produção.
- **"planeado"** — direção comprometida; o repositório ainda não existe.

Não usamos linguagem de falsa descentralização e não afirmamos prontidão
para produção onde ela não existe. Ver
[`PRODUCTION_PRINCIPLES.md`](PRODUCTION_PRINCIPLES.md) para a definição da
organização sobre prontidão.

---

## Visibilidade dos repositórios

A CubeShackles está dividida entre repositórios públicos e privados por
desenho:

- Os repositórios **públicos** apresentam arquitetura verdadeira, orientada a
  programadores. Não contêm lógica de orquestração soberana, modelos de
  IA/fraude, ferramentas para reguladores, inteligência económica nem
  segredos de produção.
- Os repositórios **privados** protegem a infraestrutura soberana, os
  modelos de IA/fraude, as ferramentas para reguladores, a inteligência
  económica e a I&D futura de Cube Silicon / Shackle Silicon.

O inventário completo está em [`REPOSITORY_MAP.md`](REPOSITORY_MAP.md) — 55
repositórios em 14 camadas, mais uma entrada interna restrita.

---

## Camadas da plataforma (resumo)

| Camada | Repositórios-chave |
|---|---|
| Contratos | `cubeshackles-contracts` |
| Fundação | CIEL · Ontology · TFE · Developer Portal · Agent |
| Modelação da realidade | `cubeshackles-terrain` |
| Sistema operativo | `cubeshackles-os` · `cubeshackles-platform-specs` |
| Protocolo e execução | core · validator-node · settlement-engine · runtime · offline-infrastructure |
| API e coordenação | node-api · network-orchestrator · integration |
| Finanças institucionais | gateway · compliance · clearing · market-infrastructure · ledger · asset-registry · tokenization · rwa-custody |
| Infraestrutura soberana | ai-runtime · ai-sdk · compute · hardware |
| Inteligência | adviser · kulifikila (crédito) |
| Acesso | phone-wedge · CubeWallet · web (Explorer) · BualaBuitu · national-transit |
| Design e DX | design-system · storybook · demo · sandbox-lab |
| Regulatório e supervisão | supervision · regulatory-reporting · security-framework |
| Operações da plataforma | provincial-topology · vault · disaster-recovery · chaos · security · operations · angola-pilot · infra · observability |

---

## Comece por aqui

| Se quer… | Leia |
|---|---|
| Compreender o ecossistema completo de repositórios | [`REPOSITORY_MAP.md`](REPOSITORY_MAP.md) |
| Compreender a arquitetura da plataforma | [`SYSTEM_ARCHITECTURE.md`](SYSTEM_ARCHITECTURE.md) |
| Compreender o que significa prontidão para produção aqui | [`PRODUCTION_PRINCIPLES.md`](PRODUCTION_PRINCIPLES.md) |
| Compreender o modelo de confiança e segurança | [`SECURITY_MODEL.md`](SECURITY_MODEL.md) |
| Compreender a tese estratégica | [`docs/sovereign-infrastructure-thesis.md`](docs/sovereign-infrastructure-thesis.md) |
| Compreender o protocolo | [`docs/protocol-overview.md`](docs/protocol-overview.md) |
| Ver o roteiro e os marcos da plataforma | [`ROADMAP.md`](ROADMAP.md) |
| Compreender o ponto de entrada para programadores | [`docs/developer-entrypoint.md`](docs/developer-entrypoint.md) |
| Compreender as regras de contrato e interoperabilidade | [`contracts/CONTRACTS.md`](contracts/CONTRACTS.md) |
| Compreender a governança e a política de repositórios | [`governance/policies/`](governance/policies/) |
| Criar ou classificar um novo repositório | [`docs/repo-governance.md`](docs/repo-governance.md) |
| Rever a auditoria de consistência da arquitetura | [`docs/architecture-consistency-audit.md`](docs/architecture-consistency-audit.md) |
| Regras de autoria e ferramentas, lideradas pelo fundador | [`governance/policies/authorship-and-tooling.md`](governance/policies/authorship-and-tooling.md) |
| Auditoria de documentação do ecossistema (revisão liderada pelo fundador) | [`docs/FOUNDER_LED_DOCUMENTATION_AUDIT.md`](docs/FOUNDER_LED_DOCUMENTATION_AUDIT.md) |
| Etiquetas do GitHub, marcos e taxonomia de commits | [`docs/GITHUB_TAXONOMY.md`](docs/GITHUB_TAXONOMY.md) |
| Contribuir | [`CONTRIBUTING.md`](CONTRIBUTING.md) |

---

## Licença e divulgação

Os termos de licenciamento são definidos por repositório. Os procedimentos de
divulgação de segurança estão descritos em
[`SECURITY_MODEL.md`](SECURITY_MODEL.md). Apenas divulgação coordenada — não
abra issues públicas descrevendo vulnerabilidades.

---

*CubeShackles — infraestrutura de coordenação soberana para sistemas
financeiros nativos de Angola.*

<!--
localization:
  canonical_file: README.md
  locale: pt-AO
  translation_status: machine-assisted
  canonical_commit: 14f730d
  last_synchronized: 2026-07-18
-->
