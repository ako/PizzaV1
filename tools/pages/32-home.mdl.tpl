mdl 1;
-- SCR-01 Home (EP-02: US-021, US-022, US-023, US-024). GENERATED from
-- tools/pages/32-home.mdl.tpl by tools/pages/gen_home_kpis.py — edit the template.

/**
 * Calculates the four home KPIs on the server (US-023, LITE-SEC-02): orders
 * deployed today, average pipeline time (paidAt → completedAt, half-up to
 * whole seconds), kitchen load of the ONLINE ovens and couriers on duty. The
 * guest receives these numbers only, never the orders behind them.
 *
 * @param $View The home view to fill
 */
create or modify microflow Shop.SUB_Home_Refresh ($View: Shop.HomeView)
folder 'Home'
begin
  declare $DayStart DateTime = beginOfDay([%CurrentDateTime%]);
  retrieve $Done from Shop.Order where [(OrderStatus = 'DELIVERED' or OrderStatus = 'PICKED_UP') and CompletedAt >= $DayStart];
  $DoneCount = count $Done;
  declare $Total Decimal = 0;
  declare $Timed Integer = 0;
  loop $D in $Done
  begin
    if $D/PaidAt != empty and $D/CompletedAt != empty then
      set $Total = $Total + secondsBetween($D/PaidAt, $D/CompletedAt);
      set $Timed = $Timed + 1;
    end if;
  end loop;
  declare $AvgText String = '—';
  if $Timed > 0 then
    $Mm = call microflow Shop.SUB_MmSs(Seconds = round($Total div $Timed));
    set $AvgText = $Mm;
  end if;
  declare $Per Integer = max(1, ceil($DoneCount div 40));
  declare $Lit Integer = ceil($DoneCount div $Per);
  retrieve $Ovens from Shop.Oven where [OvenStatus = 'ONLINE'];
  $Slots = sum $Ovens by CapacityOrders;
  retrieve $Baking from Shop.Order where [OrderStatus = 'BAKING' and Shop.Order_Oven/Shop.Oven/OvenStatus = 'ONLINE'];
  $Busy = count $Baking;
  declare $Pct Integer = 0;
  if $Slots > 0 then
    set $Pct = round($Busy * 100 div $Slots);
  end if;
  retrieve $AllCouriers from Shop.Courier;
  $CourierTotal = count $AllCouriers;
  retrieve $OnDuty from Shop.Courier where [CourierStatus != 'OFF_DUTY'];
  $OnDutyCount = count $OnDuty;
  retrieve $Published from Shop.Product where [ProductStatus = 'PUBLISHED'];
  $PublishedCount = count $Published;
  retrieve $NotOrderable from Shop.Product where [ProductStatus = 'PUBLISHED' and IsOrderable = false];
  $SoldOutCount = count $NotOrderable;
  declare $Vulns String = 'found 0 vulnerabilities';
  if $SoldOutCount = 1 then
    set $Vulns = 'found 1 sold-out module';
  end if;
  if $SoldOutCount > 1 then
    set $Vulns = 'found ' + toString($SoldOutCount) + ' sold-out modules';
  end if;
  change $View (DeployedToday = $DoneCount, PxPer = $Per, PxLit = $Lit, ScaleText = if $Per = 1 then '1 px = 1 order' else '1 px = ' + toString($Per) + ' orders',
    AvgText = $AvgText, HasAvg = $Timed > 0, Busy = $Busy, Slots = round($Slots), LoadPct = $Pct, IsHeavy = $Pct >= 85,
    CouriersOn = $OnDutyCount, CouriersTotal = $CourierTotal,
    TermModules = 'added ' + toString($PublishedCount) + ' modules from 4 registries in 2s', TermVulns = $Vulns);
end;

/**
 * Data source of the home page: KPIs and the carousel position.
 *
 * @returns A new home view
 */
create or modify microflow Shop.DS_Home ()
returns Shop.HomeView as $View
folder 'Home'
begin
  $View = create Shop.HomeView (CarouselStart = 0);
  call microflow Shop.SUB_Home_Refresh(View = $View);
  call microflow Shop.SUB_Home_CarouselPos(View = $View);
  return $View;
end;

/**
 * Carousel position label, e.g. 01–03 / 06 (TXT-MENU-62).
 *
 * @param $View The home view
 */
create or modify microflow Shop.SUB_Home_CarouselPos ($View: Shop.HomeView)
folder 'Home'
begin
  retrieve $Featured from Shop.Product where [IsFeatured = true and ProductStatus = 'PUBLISHED'];
  $N = count $Featured;
  declare $First Integer = $View/CarouselStart + 1;
  declare $Last Integer = min($View/CarouselStart + 3, $N);
  change $View (FeaturedCount = $N, CarouselPos = formatDecimal($First, '00') + '–' + formatDecimal($Last, '00') + ' / ' + formatDecimal($N, '00'));
end;

/**
 * Featured products for the carousel from the current position (US-022):
 * published and featured, in menu order; never draft or archived.
 *
 * @param $View The home view
 * @returns The products from the carousel position on
 */
create or modify microflow Shop.DS_Home_Featured ($View: Shop.HomeView)
returns List of Shop.Product as $Visible
folder 'Home'
begin
  retrieve $Featured from Shop.Product where [IsFeatured = true and ProductStatus = 'PUBLISHED'] sort by SortOrder asc;
  $Visible = range $Featured offset $View/CarouselStart;
  return $Visible;
end;

/**
 * Carousel arrows: moves one card left or right, never past the ends.
 *
 * @param $View The home view
 * @param $Step -1 or 1
 */
create or modify microflow Shop.SUB_Home_Carousel ($View: Shop.HomeView, $Step: Integer)
folder 'Home'
begin
  declare $Max Integer = max(0, $View/FeaturedCount - 3);
  change $View (CarouselStart = max(0, min($Max, $View/CarouselStart + $Step)));
  call microflow Shop.SUB_Home_CarouselPos(View = $View);
end;

/**
 * Carousel arrows: moves one card left or right, never past the ends.
 * Page entry point; the logic is in SUB_Home_Carousel.
 *
 * @param $View The home view
 * @param $Step -1 or 1
 */
create or modify microflow Shop.ACT_Home_Carousel ($View: Shop.HomeView, $Step: Integer)
folder 'Home'
begin
  call microflow Shop.SUB_Home_Carousel(View = $View, Step = $Step);
end;

/**
 * Live refresh of the home KPIs (US-023: within 10 s while the page is open).
 *
 * @param $View The home view
 */
create or modify microflow Shop.ACT_Home_Refresh ($View: Shop.HomeView)
folder 'Home'
begin
  call microflow Shop.SUB_Home_Refresh(View = $View);
end;

/** Card of a featured module in the home carousel (US-022). */
create or modify snippet Shop.SNIP_FeaturedCard (Params: ($Product: Shop.Product)) {
  container pcard (Class: 'pcard', DynamicClasses: if $Product/IsOrderable then '' else 'sold-out') {
    container pHead (Class: 'pcard-head') {
      dynamictext pHeadIcon (Content: 'data_object', Class: 'ms sm c-orange')
      dynamictext pFile (Content: '{1}', ContentParams: ({1} = $Product/ModulePath), Class: 'fname')
      dynamictext pVer (Content: '{1}', ContentParams: ({1} = $Product/VersionTag), Class: 't-micro c-green')
    }
    container pImgWrap (Class: 'pimg-wrap') {
      dynamictext pSold (Content: 'SOLD_OUT', Class: 'chip tag-sold sold-ribbon', Visible: not($Product/IsOrderable))
      container pFrame (Class: 'img-frame') {
        image pImg (ImageType: imageUrl, ImageUrl: '/assets/products/{1}', ImageUrlParams: ({1} = $Product/ImageFile), AlternativeText: '{1}', AlternativeTextParams: ({1} = $Product/ImageAlt), Class: 'pimg')
      }
    }
    container pBody (Class: 'pcard-body') {
      container pTitle (Class: 'pcard-title') {
        dynamictext pName (Content: '{1}', ContentParams: ({1} = $Product/Name), RenderMode: H3, Class: 't-h3')
        dynamictext pPrice (Content: '{1}', ContentParams: ({1} = $Product/CardPriceLabel), Class: 'price')
      }
      dynamictext pReal (Content: '{1}', ContentParams: ({1} = $Product/RealWorldName), Class: 'real')
      dynamictext pShort (Content: '{1}', ContentParams: ({1} = $Product/ShortDescription), Class: 't-body-long p-short')
      container pBadges (Class: 'row badges') {
        dynamictext bVegan (Content: '<Vegan />', Class: 'chip tag-badge', Visible: $Product/IsVegan)
        dynamictext bVeg (Content: '<Vegetarian />', Class: 'chip tag-badge', Visible: $Product/IsVegetarian and not($Product/IsVegan))
        dynamictext bClassic (Content: '<Classic />', Class: 'chip', Visible: $Product/HasBadgeClassic)
        dynamictext bBest (Content: '<BestSeller />', Class: 'chip tag-badge', Visible: $Product/HasBadgeBestSeller)
        dynamictext bNew (Content: '<NewRelease />', Class: 'chip tag-new', Visible: $Product/HasBadgeNew)
        dynamictext bChef (Content: '<ChefPick />', Class: 'chip tag-chef', Visible: $Product/HasBadgeChefPick)
        container bSpice (Class: 'chip tag-spice', Visible: $Product/SpiceLabel != '') {
          dynamictext bSpiceIcon (Content: 'local_fire_department', Class: 'ms sm')
          dynamictext bSpiceTxt (Content: '{1}', ContentParams: ({1} = $Product/SpiceLabel))
        }
      }
    }
    container pFoot (Class: 'pcard-foot') {
      actionbutton pImport (Caption: '+ import', Action: CALL MICROFLOW Shop.ACT_Product_QuickAdd(Product = $Product), Class: 'btn btn-primary', Visible: $Product/IsOrderable)
      actionbutton pSoldBtn (Caption: '404: OUT_OF_STOCK', Action: NOTHING, Class: 'btn btn-primary is-disabled', Visible: not($Product/IsOrderable))
      container pConfigure (Class: 'btn btn-ghost', OnClick: CALL MICROFLOW Shop.ACT_Configure_FromHome(Product = $Product)) {
        dynamictext pTune (Content: 'tune', Class: 'ms md')
      }
    }
  }
};

/** SCR-01 Home: hero, terminal intro, pipeline strip, live build status, featured carousel and KPIs. */
create or modify page Shop.Home (
  Title: 'Git Pizza MxDev — Architect Your Perfect Crust',
  Layout: Shop.Layout_Guest,
  Url: 'home'
) {
  dataview dvHome (DataSource: MICROFLOW Shop.DS_Home, Class: 'page-dv') {
    container page (Class: 'page scr-01 gp-live') {
      container hero (Class: 'hero') {
        container glow1 (Class: 'glow1') { }
        container glow2 (Class: 'glow2') { }
        container heroLeft (Class: 'hero-left') {
          container envChip (Class: 'env-chip') {
            container envDot (Class: 'live-dot') { }
            dynamictext envKey (Content: 'PIPELINE_OPEN //', Class: 'c-green')
            dynamictext envTxt (Content: ' Kitchen online')
          }
          container heroTitle (Class: 't-display hero-title') {
            dynamictext heroT1 (Content: 'Architect Your ', RenderMode: H1, Class: 'ht1')
            dynamictext heroT2 (Content: 'Perfect Crust', Class: 'hl')
          }
          dynamictext heroText (Content: 'Git Pizza MxDev is a Neapolitan pizza kitchen built for engineers. Pick a module, inject your toppings and deploy dinner to your door — or pull it fresh from our Mission counter.', Class: 't-body-long hero-p')
          container term (Class: 'term mt-24 hero-term') {
            container termBar (Class: 'term-bar') {
              container dots (Class: 'dots') {
                container dot1 (Class: 'dot') { }
                container dot2 (Class: 'dot') { }
                container dot3 (Class: 'dot') { }
              }
              dynamictext termTitle (Content: 'zsh — 80x24')
            }
            container termBody (Class: 'term-body') {
              container termCmd (Class: 'term-line') {
                dynamictext tArrow (Content: '➜', Class: 'c-green')
                dynamictext tHome (Content: ' ~ ', Class: 'c-primary')
                dynamictext tCmd (Content: 'npm install @git-pizza/menu')
                container tCursor (Class: 'cursor') { }
              }
              container termLines (Class: 'c-muted term-lines') {
                dynamictext tLine1 (Content: '{1}', ContentParams: ({1} = TermModules), Class: 'term-out')
                dynamictext tLine2 (Content: '{1}', ContentParams: ({1} = TermVulns), Class: 'term-out')
                dynamictext tLine3 (Content: 'Git Pizza MxDev — Mission Kitchen is online. Ready for deployment.', Class: 'term-out c-green')
              }
            }
          }
          container ctaRow (Class: 'cta-row') {
            container ctaMenu (Class: 'btn btn-primary btn-lg', OnClick: CALL MICROFLOW Shop.ACT_Nav_Menu(Category = 'PIZZAS')) {
              dynamictext ctaMenuIcon (Content: 'terminal', Class: 'ms')
              dynamictext ctaMenuTxt (Content: 'git checkout menu')
            }
            container ctaTrack (Class: 'btn btn-secondary btn-lg', OnClick: CALL MICROFLOW Shop.ACT_Nav_Track) {
              dynamictext ctaTrackIcon (Content: 'receipt_long', Class: 'ms')
              dynamictext ctaTrackTxt (Content: './track.log')
            }
          }
        }
        image heroLogo (ImageType: imageUrl, ImageUrl: '/assets/brand/logo-mark.svg', AlternativeText: 'Git Pizza MxDev logo', Class: 'hero-logo')
      }
      container pipeStrip (Class: 'pipe-strip') {
        container ps1 (Class: 'ps') {
          image ps1Img (ImageType: imageUrl, ImageUrl: '/assets/icons/icon-pizza-module.svg', AlternativeText: '', Class: 'ps-img')
          container ps1Txt {
            dynamictext ps1T (Content: '1 · import', Class: 't-label c-primary')
            dynamictext ps1S (Content: 'Pick a module and inject your toppings.', Class: 't-small c-secondary')
          }
        }
        container ps2 (Class: 'ps') {
          image ps2Img (ImageType: imageUrl, ImageUrl: '/assets/icons/icon-terminal-cli.svg', AlternativeText: '', Class: 'ps-img')
          container ps2Txt {
            dynamictext ps2T (Content: '2 · deploy', Class: 't-label c-primary')
            dynamictext ps2S (Content: 'Execute the order. Payment is simulated.', Class: 't-small c-secondary')
          }
        }
        container ps3 (Class: 'ps') {
          image ps3Img (ImageType: imageUrl, ImageUrl: '/assets/icons/icon-ci-cd-pipeline.svg', AlternativeText: '', Class: 'ps-img')
          container ps3Txt {
            dynamictext ps3T (Content: '3 · track', Class: 't-label c-primary')
            dynamictext ps3S (Content: 'Watch the pipeline: oven, QA, courier.', Class: 't-small c-secondary')
          }
        }
      }
      snippetcall scActive (Snippet: Shop.SNIP_HomeActiveOrder)
      container featured (Class: 'featured') {
        container featHead (Class: 'feat-head') {
          container featTitle {
            dynamictext featH (Content: 'Available Modules', RenderMode: H2, Class: 't-h2')
            dynamictext featSub (Content: 'Hand-picked builds from the Mission Kitchen, ready to import.', Class: 't-small c-muted feat-sub')
          }
          container carNav (Class: 'car-nav hide-phone') {
            container carPos (Class: 'car-pos') {
              dynamictext carPosTxt (Content: '{1}', ContentParams: ({1} = CarouselPos), Class: 'car-pos-txt')
            }
            container carPrev (Class: 'car-btn', DynamicClasses: if $currentObject/CarouselStart = 0 then 'is-disabled' else '', OnClick: CALL MICROFLOW Shop.ACT_Home_Carousel(View = $currentObject, Step = -1)) {
              dynamictext carPrevIcon (Content: 'chevron_left', Class: 'ms')
            }
            container carNext (Class: 'car-btn', DynamicClasses: if $currentObject/CarouselStart >= $currentObject/FeaturedCount - 3 then 'is-disabled' else '', OnClick: CALL MICROFLOW Shop.ACT_Home_Carousel(View = $currentObject, Step = 1)) {
              dynamictext carNextIcon (Content: 'chevron_right', Class: 'ms')
            }
          }
        }
        listview lvFeatured (DataSource: MICROFLOW Shop.DS_Home_Featured(View = $currentObject), PageSize: 200, Class: 'carousel') {
          snippetcall scCard (Snippet: Shop.SNIP_FeaturedCard, Params: (Product = $currentObject))
        }
      }
      container kpis (Class: 'kpis') {
        container kpi1 (Class: 'kpi') {
          container kpi1H (Class: 'h') {
            dynamictext kpi1Icon (Content: 'rocket_launch', Class: 'ms')
            dynamictext kpi1L (Content: 'DEPLOYED_TODAY', Class: 'lbl')
            container kpi1Live (Class: 'live') {
              container kpi1Dot (Class: 'live-dot') { }
              dynamictext kpi1LiveT (Content: 'LIVE')
            }
          }
          dynamictext kpi1V (Content: '{1}', ContentParams: ({1} = if $currentObject/DeployedToday = 0 then '—' else toString($currentObject/DeployedToday)), Class: 'v')
          container kpi1Px (Class: 'px') {
%%PIXELS%%
          }
          dynamictext kpi1Sub (Content: '{1}', ContentParams: ({1} = ScaleText), Class: 'sub')
        }
        container kpi2 (Class: 'kpi') {
          container kpi2H (Class: 'h') {
            dynamictext kpi2Icon (Content: 'timer', Class: 'ms')
            dynamictext kpi2L (Content: 'AVG_PIPELINE_TIME', Class: 'lbl')
          }
          dynamictext kpi2V (Content: '{1}', ContentParams: ({1} = AvgText), Class: 'v')
          container kpi2Pipe {
            container kpi2Bars (Class: 'pipe', DynamicClasses: if $currentObject/HasAvg then '' else 'off') {
              container pb1 (Class: 'pb') { }
              container pb2 (Class: 'pb') { }
              container pb3 (Class: 'pb') { }
              container pb4 (Class: 'pb') { }
              container pb5 (Class: 'pb') { }
            }
            container kpi2Pl (Class: 'pl') {
              dynamictext pl1 (Content: 'QUEUED')
              dynamictext pl2 (Content: 'BAKING')
              dynamictext pl3 (Content: 'QA')
              dynamictext pl4 (Content: 'DISPATCH')
              dynamictext pl5 (Content: 'DEPLOYED')
            }
          }
        }
        container kpi3 (Class: 'kpi') {
          container kpi3H (Class: 'h') {
            dynamictext kpi3Icon (Content: 'local_fire_department', Class: 'ms')
            dynamictext kpi3L (Content: 'KITCHEN_LOAD', Class: 'lbl')
            dynamictext kpi3Heavy (Content: 'HEAVY', Class: 'chip tag-spice heavy', Visible: $currentObject/IsHeavy)
          }
          container kpi3V (Class: 'v') {
            dynamictext kpi3Val (Content: '{1}/{2}', ContentParams: ({1} = Busy, {2} = Slots))
            dynamictext kpi3Pct (Content: '· {1}%', ContentParams: ({1} = LoadPct), Class: 'small')
          }
          container kpi3Units (Class: 'units') {
%%OVENS%%
          }
        }
        container kpi4 (Class: 'kpi') {
          container kpi4H (Class: 'h') {
            dynamictext kpi4Icon (Content: 'electric_moped', Class: 'ms')
            dynamictext kpi4L (Content: 'COURIERS_ON_DUTY', Class: 'lbl')
          }
          dynamictext kpi4V (Content: '{1}', ContentParams: ({1} = CouriersOn), Class: 'v')
          container kpi4Units (Class: 'units green') {
%%COURIERS%%
          }
        }
      }
      dynamictext kpiNote (Content: 'Demo KPIs are read from the live demo data (simulated orders included). Values shown are an example.', Class: 't-micro c-muted mt-8 kpi-note')
      container liveHome (Class: 'gp-poll', OnClick: CALL MICROFLOW Shop.ACT_Home_Refresh(View = $currentObject)) { }
    }
  }
};
