import {
  getChampWinnersCategories,
  getChampWinnersNominations,
} from 'common/shared/api/champs';
import { Layout } from 'common/shared/ui/layout';
import { useAtomValue } from 'jotai';
import router from 'next/router';
import { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { champAtom } from 'store';
import styles from './ChampResultPage.module.scss';
import { declineNumberOfBalls } from 'common/shared/helpers';
import { Loader } from 'common/shared/ui/loader';
import { getUserIsOrganizer } from 'common/shared/constants';

function ChampResultPage() {
  const champ = useAtomValue(champAtom);
  const [isClient, setIsClient] = useState(false);
  const [openNominationsCategories, setOpenNominationsCategories] = useState<Record<number, boolean>>({});
  const [openNominations, setOpenNominations] = useState<Record<number, boolean>>({});
  const [openCategories, setOpenCategories] = useState<Record<number, boolean>>({});
  const USER_IS_ORGANIZER = getUserIsOrganizer();

  useEffect(() => {
    setIsClient(true);
    if (!USER_IS_ORGANIZER) {
      router.replace('/profile-edit');
    }
  }, [USER_IS_ORGANIZER]);

  const { data: champWinnersNominationsData, isLoading: isNominationsLoading } =
    useQuery(
      ['champWinnersNominations', champ?.id],
      () => getChampWinnersNominations(champ?.id!),
      {
        enabled: !!champ,
      }
    );
  const { data: champWinnersCategoriesData, isLoading: isCategoriesLoading } =
    useQuery(
      ['champWinnersCategories', champ?.id],
      () => getChampWinnersCategories(champ?.id!),
      {
        enabled: !!champ,
      }
    );

  const champWinnersCategories = champWinnersCategoriesData?.data;
  const champWinnersNominations = champWinnersNominationsData?.data;
  const isLoading = isNominationsLoading || isCategoriesLoading;

  const toggleNominationCategory = (index: number) => {
    setOpenNominationsCategories((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const toggleNomination = (index: number) => {
    setOpenNominations((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const toggleCategory = (index: number) => {
    setOpenCategories((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  return (
    <Layout pageTitle={'Результаты чемпионата'}>
      {!isLoading && isClient ? (
        <>
          <ul className={styles.nominations_categories__list}>
            <li className={styles.nominations_categories__item}>
              <h1 className={styles.nominations_categories__title}>
                Победители Номинаций
              </h1>
              {champWinnersNominations?.map((nomination, index) => (
                <div key={index}>
                  <h2
                    className={`${styles.nominations_categories__nomination} ${openNominationsCategories[index] ? styles.active : ''}`}
                    onClick={() => toggleNominationCategory(index)}
                  >
                    {nomination.category}
                  </h2>
                  {openNominationsCategories[index] && (
                    <div>
                      <h3
                        className={`${styles.nominations_categories__nomination} ${openNominations[index] ? styles.active : ''}`}
                        onClick={() => toggleNomination(index)}
                      >
                        {nomination.name}
                      </h3>
                      {openNominations[index] && (
                        <div>
                          {nomination.members.map((member, memberIndex) => (
                            <div key={memberIndex}>
                              <h4
                                className={styles.nominations_categories__member_name}
                              >
                                {member.member}
                              </h4>
                              <h4 className={styles.nominations_categories__result}>
                                Результат: {member.result_all}{' '}
                                {declineNumberOfBalls(member.result_all)}
                              </h4>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </li>
            <li className={styles.nominations_categories__item}>
              <h1 className={styles.nominations_categories__title}>
                Победители Гран-при
              </h1>
              {champWinnersCategories?.map((category, index) => (
                <div key={index}>
                  <h2
                    className={`${styles.nominations_categories__nomination} ${openCategories[index] ? styles.active : ''}`}
                    onClick={() => toggleCategory(index)}
                  >
                    {category.name}
                  </h2>
                  {openCategories[index] && (
                    <div>
                      {category.members.map((member, memberIndex) => (
                        <div key={memberIndex}>
                          <h3
                            className={styles.nominations_categories__member_name}
                          >
                            {member.member}
                          </h3>
                          <h3 className={styles.nominations_categories__result}>
                            Результат: {member.result_all}{' '}
                            {declineNumberOfBalls(member.result_all)}
                          </h3>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </li>
          </ul>
        </>
      ) : (
        <Loader fullPage />
      )}
    </Layout>
  );
}

export default ChampResultPage;
