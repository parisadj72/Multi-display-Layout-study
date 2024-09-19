using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PracticePuzzleLayout : MonoBehaviour
{
    private List<PracticeView> views = new List<PracticeView>();
    private List<Texture2D> modelTextures = new List<Texture2D>();
    private List<int> modelIcons = new List<int>();
    private List<int> modelOrder = new List<int>();

    List<Texture> texlistOns = new List<Texture>();

    public List<PracticeView> Views { get => views; set => views = value; }
    public List<int> ModelOrder { get => modelOrder; set => modelOrder = value; }
    public List<Texture> TexlistOns { get => texlistOns; set => texlistOns = value; }
    public List<Texture2D> ModelTextures { get => modelTextures; set => modelTextures = value; }
    public List<int> ModelIcons { get => modelIcons; set => modelIcons = value; }

    private void Awake()
    {
        InitializeLayout();
    }

    private void InitializeLayout()
    {
        Transform[] childTransforms = GetComponentsInChildren<Transform>();

        foreach (Transform childTransform in childTransforms)
        {
            PracticeView view = childTransform.GetComponent<PracticeView>();

            if (view != null)
            {
                views.Add(view);
                //print("View added");
            }
        }
    }

    public void CopyFields(List<Texture2D> texList, List<int> icons, List<int> viewOrder)
    {
        for (int i = 0; i < views.Count; i++)
        {
            modelTextures.Add(texList[i]);
            modelIcons.Add(icons[i]);
            modelOrder.Add(viewOrder[i]);
            //print(modelTextures[i].name);
        }

        for (int i = 0; i < views.Count; i++)
        {
            views[i].RawIcon.texture = modelTextures[modelIcons[i]];
            //print("Icons index: " + modelIcons[i]);
        }

        int selections = (views.Count / 3) + 1;

        for (int i = 0; i < selections; i++)
        {
            views[modelOrder[i]].TurnOn(true, false);
        }

        for (int i = 0; i < selections; i++)
        {
            texlistOns.Add(views[modelOrder[i]].RawIcon.texture);
        }

        List<Texture> copy = new List<Texture>();

        for (int i = 0; i < texlistOns.Count; i++)
        {
            Texture tex = texlistOns[i];
            copy.Add(tex);
        }

        texlistOns = RandomGenerator.shuffleList(texlistOns);

        for (int i = 0; i < selections; i++)
        {
            views[modelOrder[i]].RawIcon.texture = texlistOns[i];
        }


        //print("3 or 6-view layout is present");
        for (int i = 0; i < copy.Count; ++i)
        {
            if (!views[i].IsOn)
            {
                continue;
            }
            else
            {
                if (copy[i].name.Equals(texlistOns[i].name))
                {
                    print("Icons are the same. Shuffle again");
                    while (copy[i].name.Equals(texlistOns[i].name))
                    {
                        texlistOns = RandomGenerator.shuffleList(texlistOns);
                    }
                }
            }
        }

        for (int i = 0; i < selections; i++)
        {
            views[modelOrder[i]].RawIcon.texture = texlistOns[i];
        }
    }
}
